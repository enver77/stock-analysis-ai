import os
import shutil
from huggingface_hub import HfApi

def deploy():
    print("🚀 Preparing API Deployment...")
    
    # 1. Ask for Info
    token = input("Paste Hugging Face WRITE Token: ").strip()
    repo_id = input("Paste API Space Repo ID (e.g. envererman08/stock-analysis-api): ").strip()

    # 2. Copy Files to deploy folder
    deploy_dir = "stock_api_deploy"
    source_dir = "stock"
    
    files_to_copy = [
        "api.py",
        "data_layer.py", 
        "analysis_layer.py",
        "adaboost_model.joblib",
        "scaler.joblib"
    ]
    
    print(f"\n📦 Copying files to {deploy_dir}...")
    for f in files_to_copy:
        try:
            # Try stock/ folder first
            src = os.path.join(source_dir, f)
            if not os.path.exists(src):
                # Try root folder
                src = f
            
            shutil.copy2(src, os.path.join(deploy_dir, f))
            print(f"✅ Copied {f}")
        except Exception as e:
            print(f"❌ Failed to copy {f}: {e}")
            
    # Copy metadata from root
    try:
        shutil.copy2("model_metadata.json", os.path.join(deploy_dir, "model_metadata.json"))
        print("✅ Copied model_metadata.json")
    except:
        pass # Optional

    # 3. Upload
    print(f"\n☁️ Uploading to {repo_id}...")
    try:
        api = HfApi(token=token)
        api.upload_folder(
            folder_path=deploy_dir,
            repo_id=repo_id,
            repo_type="space",
            commit_message="Deploy FastAPI Backend"
        )
        print("\n🎉 API DEPLOYMENT SUCCESSFUL!")
        print(f"👉 your API Docs: https://huggingface.co/spaces/{repo_id}/docs")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    deploy()
