from ask_gemini_with_history import ask_gemini_with_history
import json
import requests
from requests.auth import HTTPBasicAuth
import time

def trigger_jenkins_and_get_error_log():
    # Jenkins server details
    JENKINS_URL = 'http://localhost:8080'
    JOB_NAME = 'Self_Healing_CI'  # Replace with your job name
    API_TOKEN = '113716623888a198fd6144d1cd92d47ec7'
    USERNAME = 'admin'
    BUILD_TOKEN = 'mytoken123'  # Token you set in the job config

    try:
        # Get crumb for CSRF protection
        crumb_url = f"{JENKINS_URL}/crumbIssuer/api/json"
        crumb_response = requests.get(crumb_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
        crumb_response.raise_for_status()
        crumb_data = crumb_response.json()
        headers = {
            crumb_data['crumbRequestField']: crumb_data['crumb']
        }

        # Trigger the build
        build_url = f"{JENKINS_URL}/job/{JOB_NAME}/build?token={BUILD_TOKEN}"
        trigger_response = requests.post(build_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN), headers=headers)

        if trigger_response.status_code != 201:
            print(f"❌ Failed to trigger build: {trigger_response.status_code}")
            print(trigger_response.text)
            return None

        # Get queue location
        queue_location = trigger_response.headers.get('Location')
        if not queue_location:
            print("❌ Could not get queue location from response.")
            return None

        print(f"🚀 Build queued at: {queue_location}")

        # Poll Jenkins queue for build number
        while True:
            queue_data = requests.get(f"{queue_location}api/json", auth=HTTPBasicAuth(USERNAME, API_TOKEN)).json()

            if queue_data.get('cancelled'):
                print("❌ Build was cancelled from Jenkins UI.")
                return None

            executable = queue_data.get('executable')
            if executable:
                build_number = executable['number']
                print(f"✅ Build has started! Build number: {build_number}")
                break
            else:
                print("⏳ Waiting for Jenkins to assign build number...")
                time.sleep(2)

        # Poll for build completion
        build_status_url = f"{JENKINS_URL}/job/{JOB_NAME}/{build_number}/api/json"
        error_log = ""
        while True:
            build_data = requests.get(build_status_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN)).json()
            if build_data.get('building'):
                print("🔧 Build is still running...")
                time.sleep(3)
            else:
                result = build_data.get('result')
                if result == "SUCCESS":
                    print("✅ Build passed!")
                    return ""
                else:
                    print(f"❌ Build failed with status: {result}")
                    # Fetch and return console log
                    log_url = f"{JENKINS_URL}/job/{JOB_NAME}/{build_number}/consoleText"
                    log_response = requests.get(log_url, auth=HTTPBasicAuth(USERNAME, API_TOKEN))
                    error_log = log_response.text
                    #print("\n📄 Console Output:\n")
                    #print(error_log)
                    return error_log

    except Exception as e:
        print(f"⚠️ Exception occurred: {e}")
        return None



def clean_gemini_response(gemini_text):
    # Remove triple backticks and optional language tag (e.g., ```java)
    lines = gemini_text.strip().splitlines()
    if lines[0].strip().startswith("```"):
        lines = lines[1:]  # Remove first line
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]  # Remove last line
    return "\n".join(lines)



if __name__ == "__main__":
    while True:
        error_log = trigger_jenkins_and_get_error_log()
        if error_log:
            print("\n🔍 Build failed. Error log captured.\n")
            #print(error_log)
            # 🔁 Now you can pass `error_log` to Gemini, etc.
            prompt_2 = (
                f"Below is a Jenkins build error log '{error_log}'\n. Identify the full path of the file in my codebase that caused the error. Return only the most relevant file path(s), without extra explanation."
                )
            response_text_2 = ask_gemini_with_history(prompt_2)
            #print(response_text_2)
            actual_file_path = response_text_2.strip()
            print(f"📂 File causing error: {actual_file_path}\n")
            try:
                with open(actual_file_path, "r") as f:
                    file_code = f.read()
                #print(file_code)  # or send it to Gemini
            except FileNotFoundError:
                print(f"File not found: {actual_file_path}")
                break
            except Exception as e:
                print(f"Error reading file: {e}")
                break
            prompt_1 = (
                f"Here is the error from jenkins: '{error_log}'\n and the code file '{file_code}'\n"
                "Please analyze the error and update the code accordingly. Return the full corrected version of the code file, with all necessary fixes applied. Do not explain anything — just return the complete updated code so I can paste it directly."
                )
            response_text_1 = clean_gemini_response(ask_gemini_with_history(prompt_1))
            with open(actual_file_path, "w") as f:
                f.write(response_text_1)
            #print(response_text_1)
        elif error_log == "":
            print("\n✅ Build passed. No errors to report.\n")
            break  # Exit the loop since we can't proceed
        else:
            print("\n⚠️ Could not retrieve build info or error log.\n")
            break  # Exit the loop since we can't proceed
