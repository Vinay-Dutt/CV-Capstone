import os
import urllib.request
import subprocess
import sys

def download_file(url, dest):
    print(f"Downloading {url} ...")
    urllib.request.urlretrieve(url, dest)

def setup_gradle_wrapper():
    wrapper_dir = os.path.join("android-wrapper", "gradle", "wrapper")
    os.makedirs(wrapper_dir, exist_ok=True)
    
    props_path = os.path.join(wrapper_dir, "gradle-wrapper.properties")
    target_version = "8.5"
    needs_clean = True
    
    if os.path.exists(props_path):
        with open(props_path, "r") as f:
            content = f.read()
            if f"gradle-{target_version}-bin.zip" in content:
                needs_clean = False
                
    if needs_clean:
        print(f"Cleaning existing Gradle files to update to Gradle {target_version}...")
        for path in [
            props_path,
            os.path.join("android-wrapper", "gradlew.bat"),
            os.path.join("android-wrapper", "gradlew"),
            os.path.join(wrapper_dir, "gradle-wrapper.jar")
        ]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Warning: Could not remove {path}: {e}")
    
    # 1. Write gradle-wrapper.properties
    props_content = (
        "distributionBase=GRADLE_USER_HOME\n"
        "distributionPath=wrapper/dists\n"
        "distributionUrl=https\\://services.gradle.org/distributions/gradle-8.5-bin.zip\n"
        "zipStoreBase=GRADLE_USER_HOME\n"
        "zipStorePath=wrapper/dists\n"
    )
    with open(props_path, "w") as f:
        f.write(props_content)
    print("Created gradle-wrapper.properties")
    
    # 2. Download gradlew.bat
    gradlew_bat_path = os.path.join("android-wrapper", "gradlew.bat")
    if not os.path.exists(gradlew_bat_path):
        download_file("https://raw.githubusercontent.com/gradle/gradle/master/gradlew.bat", gradlew_bat_path)
        
    # 3. Download gradlew (Unix)
    gradlew_path = os.path.join("android-wrapper", "gradlew")
    if not os.path.exists(gradlew_path):
        download_file("https://raw.githubusercontent.com/gradle/gradle/master/gradlew", gradlew_path)
        if os.name != 'nt':
            os.chmod(gradlew_path, 0o755)
            
    # 4. Download gradle-wrapper.jar
    jar_path = os.path.join(wrapper_dir, "gradle-wrapper.jar")
    if not os.path.exists(jar_path):
        download_file("https://raw.githubusercontent.com/gradle/gradle/master/gradle/wrapper/gradle-wrapper.jar", jar_path)

def setup_local_properties():
    props_path = os.path.join("android-wrapper", "local.properties")
    sdk_path = r"C:\Users\VINAY\AppData\Local\Android\Sdk"
    sdk_path_escaped = sdk_path.replace("\\", "\\\\").replace(":", "\\:")
    
    with open(props_path, "w") as f:
        f.write(f"sdk.dir={sdk_path_escaped}\n")
    print(f"Created local.properties pointing to {sdk_path}")

def run_build():
    print("Building APK using Gradle...")
    cwd = os.path.join(os.getcwd(), "android-wrapper")
    cmd = ["cmd.exe", "/c", "gradlew.bat", "assembleDebug"]
    if os.name != 'nt':
        cmd = ["./gradlew", "assembleDebug"]
        
    # Configure JAVA_HOME to use Android Studio's bundled JDK (JBR) to avoid JDK 25 incompatibilities
    env = os.environ.copy()
    studio_jbr = r"C:\Program Files\Android\Android Studio\jbr"
    if os.path.exists(studio_jbr):
        print(f"Setting JAVA_HOME to Android Studio bundled JBR: {studio_jbr}")
        env["JAVA_HOME"] = studio_jbr
    else:
        print("Warning: Android Studio bundled JBR not found, attempting to use system Java.")
        
    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    for line in process.stdout:
        print(line.strip())
    process.wait()
    
    if process.returncode == 0:
        print("BUILD SUCCESSFUL!")
        apk_src = os.path.join("android-wrapper", "app", "build", "outputs", "apk", "debug", "app-debug.apk")
        apk_dest = os.path.join(os.getcwd(), "CV-Capstone-app.apk")
        if os.path.exists(apk_src):
            if os.path.exists(apk_dest):
                os.remove(apk_dest)
            os.rename(apk_src, apk_dest)
            print(f"\n==================================================================")
            print(" APK GENERATED SUCCESSFULLY!")
            print(f" Saved to: {apk_dest}")
            print(" You can find 'CV-Capstone-app.apk' in your file manager!")
            print("==================================================================\n")
    else:
        print("BUILD FAILED! Please check the errors above.")

if __name__ == "__main__":
    setup_gradle_wrapper()
    setup_local_properties()
    run_build()
