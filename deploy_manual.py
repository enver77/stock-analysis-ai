import os
import shutil
from huggingface_hub import HfApi

def deploy():
    print("🚀 Starting Manual Deployment Test...")
    
    # 1. Ask for credentials
    token = input("Please paste your Hugging Face WRITE Token (hf_...): ").strip()
    repo_id = input("Please paste your Space Repo ID (e.g., envererman08/stock-analysis-ai): ").strip()
    
    if not token.startswith("hf_"):
        print("❌ Error: Token must start with 'hf_'")
        return

    # 2. Prepare Stock folder
    print("\n📦 Preparing files in 'stock' folder...")
    target_dir = "stock"
    
    # Check if app file exists
    src_app = os.path.join(target_dir, "huggingface_app.py")
    dest_app = os.path.join(target_dir, "app.py")
    
    if os.path.exists(src_app):
        shutil.copy2(src_app, dest_app)
        print(f"✅ Copied {src_app} -> {dest_app}")
    else:
        print(f"⚠️ Warning: Could not find {src_app}")

    # Check requirements
    src_req = os.path.join(target_dir, "requirements_hf.txt")
    dest_req = os.path.join(target_dir, "requirements.txt")
    
    if os.path.exists(src_req):
        shutil.copy2(src_req, dest_req)
        print(f"✅ Copied {src_req} -> {dest_req}")

    # 3. Attempt Upload
    print(f"\n☁️ Attempting upload to {repo_id}...")
    try:
        api = HfApi(token=token)
        
        # Verify Identity
        user = api.whoami()
        print(f"✅ Authenticated as: {user['name']} (Type: {user['type']})")
        
        # Upload
        api.upload_folder(
            folder_path=target_dir,
            repo_id=repo_id,
            repo_type="space",
            ignore_patterns=["__pycache__", "*.git*", "Dockerfile*"],
            commit_message="Manual Deployment Test"
        )
        print("\n🎉 SUCCESS! Deployment worked. The issue is likely GitHub Secrets configuration.")
        
    except Exception as e:
        print(f"\n❌ DEPLOYMENT FAILED!")
        print(f"Error Details: {e}")
        print("\nCommon fixes:")
        print("1. If 404: The Repo ID is wrong.")
        print("2. If 403: The Token is 'Read-only'. You need a WRITE token.")

if __name__ == "__main__":
    try:
        deploy()
    except KeyboardInterrupt:
        print("\nCancelled.")
