#!/usr/bin/env python3
import base64, json, os, sys, time
from algosdk import account, mnemonic, transaction as txn
from algosdk.v2client import algod
from algosdk.encoding import decode_address


ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
HEADERS = {}

ADMIN_MNEMONIC   = """day best ocean hello gesture steak toilet obscure sail regret afford sample muscle buyer faith say theme scene harsh category mom claw ten about miss"""
STUDENT_MNEMONIC = """woman scale phrase door obscure inspire shed danger book lift helmet armor sign stable assume keep blade bench frequent pizza purity spot fresh abstract route"""
OFFICER_MNEMONIC = """earth dragon inflict paper inject buffalo minute harvest huge phone power keen remain effort cricket wide useless day matrix knock opera pudding pyramid above bird"""  



def normalize_mnemonic(raw: str) -> str:
    return " ".join(raw.strip().split())

def load_account(mnemonic_raw: str):
    mn = normalize_mnemonic(mnemonic_raw)
    words = mn.split()
    if len(words) != 25:
        raise ValueError(f"Mnemonic tiene {len(words)} palabras (debe ser 25).")
    sk = mnemonic.to_private_key(mn)
    addr = account.address_from_private_key(sk)
    return sk, addr

def sha256_file(path: str) -> bytes:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.digest()

def compile_teal(filepath: str, client) -> bytes:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No existe TEAL: {filepath}")
    with open(filepath, "r") as f:
        src = f.read()
    resp = client.compile(src)
    return base64.b64decode(resp["result"])

# COnexion

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, HEADERS)


def sign_document(signer_sk, signer_addr, app_id, doc_hash_bytes, client=None):
    """Send an app call to sign the document on-chain.

    Parameters:
      - signer_sk, signer_addr: keypair
      - app_id: application id
      - doc_hash_bytes: bytes SHA256 of document
      - client: optional algod client (defaults to module client)
    """
    if client is None:
        client = algod_client
    params = client.suggested_params()
    txn_call = txn.ApplicationNoOpTxn(
        sender=signer_addr,
        sp=params,
        index=app_id,
        app_args=[doc_hash_bytes]
    )
    signed_txn = txn_call.sign(signer_sk)
    txid = client.send_transaction(signed_txn)
    print("➤ Tx enviada:", txid)
    txn.wait_for_confirmation(client, txid, 4)
    print("   Documento firmado por:", signer_addr)


def deploy_contract(admin_mnemonic, student_mnemonic, officer_mnemonic, doc_path, teal_dir=None):
    """Deploy the application using provided mnemonics and document path. Returns (app_id, doc_hash).

    This function can be called from other code. It will compile TEAL from teal_dir (defaults relative).
    """
    admin_sk, admin_addr = load_account(admin_mnemonic)
    student_sk, student_addr = load_account(student_mnemonic)
    officer_sk, officer_addr = load_account(officer_mnemonic)

    # If the provided document path does not exist, look for it in proyecto_creditos/src/docs/
    if not os.path.exists(doc_path):
        # Try to find it in proyecto_creditos/src/docs/ (relative to this file)
        src_docs = os.path.join(os.path.dirname(__file__), 'docs', 'plan_estudios.pdf')
        if os.path.exists(src_docs):
            doc_path = src_docs
        else:
            raise FileNotFoundError(f"No se encontró documento en {doc_path} ni en {src_docs}")

    doc_hash = sha256_file(doc_path)

    # find teal files relative to this module if not provided
    base = os.path.dirname(__file__)
    teal_dir = teal_dir or os.path.join(base, '..', 'teal')
    approval_prog = compile_teal(os.path.join(teal_dir, 'student_contract.teal'), algod_client)
    clear_prog = compile_teal(os.path.join(teal_dir, 'clear_state.teal'), algod_client)

    student_id = b"2025A00123"
    global_schema = txn.StateSchema(num_uints=6, num_byte_slices=4)
    local_schema = txn.StateSchema(num_uints=0, num_byte_slices=0)

    app_args = [doc_hash, decode_address(student_addr), decode_address(officer_addr), student_id]

    params = algod_client.suggested_params()
    create_txn = txn.ApplicationCreateTxn(
        sender=admin_addr,
        sp=params,
        on_complete=txn.OnComplete.NoOpOC,
        approval_program=approval_prog,
        clear_program=clear_prog,
        global_schema=global_schema,
        local_schema=local_schema,
        app_args=app_args,
    )
    signed_create = create_txn.sign(admin_sk)
    txid = algod_client.send_transaction(signed_create)
    txn.wait_for_confirmation(algod_client, txid, 4)
    info = algod_client.pending_transaction_info(txid)
    app_id = info["application-index"]
    return app_id, doc_hash


if __name__ == '__main__':
    # legacy behavior when run as script: deploy and sign using constants above
    admin_sk, admin_addr = load_account(ADMIN_MNEMONIC)
    student_sk, student_addr = load_account(STUDENT_MNEMONIC)
    officer_sk, officer_addr = load_account(OFFICER_MNEMONIC)

    print("[+] Admin:", admin_addr)
    print("[+] Student:", student_addr)
    print("[+] Officer:", officer_addr)

    DOC_PATH = os.path.abspath("docs/plan_estudios.pdf")
    if not os.path.exists(DOC_PATH):
        # try to find it in proyecto_creditos/src/docs/ instead
        src_path = os.path.join(os.path.dirname(__file__), 'docs', 'plan_estudios.pdf')
        if os.path.exists(src_path):
            DOC_PATH = src_path
        else:
            raise FileNotFoundError(f"No se encontró documento en {DOC_PATH} ni en {src_path}")

    doc_hash = sha256_file(DOC_PATH)
    print("[+] Hash del documento:", doc_hash.hex())

    # To avoid accidental network operations, only deploy/sign when SMART_CONTRACT_AUTO_RUN=1
    if os.getenv('SMART_CONTRACT_AUTO_RUN', '0') == '1':
        app_id, _ = deploy_contract(ADMIN_MNEMONIC, STUDENT_MNEMONIC, OFFICER_MNEMONIC, DOC_PATH)
        print("[+] Aplicación creada, ID =", app_id)
        # perform signatures
        sign_document(student_sk, student_addr, app_id, doc_hash)
        sign_document(officer_sk, officer_addr, app_id, doc_hash)
    else:
        print("DOC_PATH creado/confirmado:", DOC_PATH)
        print("Set SMART_CONTRACT_AUTO_RUN=1 to perform deploy/sign (use with caution).")

