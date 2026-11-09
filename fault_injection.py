import random
import subprocess
import time

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

print("Starting fault-injection build loop...")

# Hum 5 test builds run karenge (aap isko loop mein 100-150 tak chala sakti hain)
for i in range(1, 6):
    print(f"\n--- Running Build Iteration {i} ---")
    
    # Randomly decide karein ki build fail karna hai ya pass
    should_fail = random.choice([True, False])
    
    test_file = "tests/test_main.py"
    
    if should_fail:
        print("Injecting fault: Modifying test to fail...")
        # Jaan-bujhkar test mein galat assertion daal rahe hain
        with open(test_file, "a") as f:
            f.write("\ndef test_injected_failure():\n    assert False\n")
    else:
        print("Running normal successful build...")
        # Normal change
        with open("README.md", "a") as f:
            f.write(f"\n<!-- update {i} -->")

    # Git commit and push to trigger Cloud Build
    run_cmd("git add .")
    run_cmd(f'git commit -m "Fault injection test run {i} (fail={should_fail})"')
    run_cmd("git push origin main")
    
    print("Build triggered. Waiting 30 seconds for Cloud Build...")
    time.sleep(30)
    
    # Agar fault inject kiya tha, toh git checkout se code wapas normal kar lein
    if should_fail:
        run_cmd("git checkout tests/test_main.py")
        run_cmd("git add tests/test_main.py")
        run_cmd('git commit -m "Revert injected fault"')
        run_cmd("git push origin main")
        time.sleep(20)

print("Fault injection batch completed!")
