cd ~/agentic-cicd
cat << 'EOF' > EXPLANATION.md
# Agentic CI/CD Pipeline - Simple Guide & Step-by-Step Explanation

Yeh document isiliye banaya gaya hai taaki aapko samajh aaye ki is poore project mein kaun sa step kyun kiya gaya, IAM permissions ka kya kaam hai, aur har ek choti cheez ka kya matlab hai.

---

## 1. Project Ka Matlab Kya Hai? (Overview)
Hum ek aisi **CI/CD Pipeline** bana rahe hain jo GitHub par code push hote hi ya build run karte hi:
1. Automatically code ke tests run kare (`pytest`).
2. Code ka Docker container banaye.
3. Use Google Cloud Run par live (deploy) karde.
4. Build ka status aur logs automatically **BigQuery** database mein save karde taaki hum track kar sakein ki build pass hua ya fail.

---

## 2. Step-by-Step Poora Process aur Wajah (Why we did it?)

### Step 0: Test Files Clean Karna (`tests/test_main.py`)
* **Kyun kiya:** Shuruat mein test file mein ek aisi test thi jo jaan-bujhkar fail ho rahi thi (`assert False`). Pytest check karta hai ki saare tests pass hone chahiye, isiliye test fail hone par build bhi ruk raha tha. Humne use theek kiya taaki tests pass ho sakein.

### Step 1: Cloud Run Service Deploy Karna (`Step #3` in Cloud Build)
* **Kyun kiya:** Hamari app ko internet par live lana zaroori tha taaki koi bhi use access kar sake. Iske liye humne Google Cloud Run ka use kiya aur ise Mumbai region (`asia-south1`) mein deploy kiya. Iska live URL bhi mil gaya.

### Step 2: BigQuery Dataset Banana (`cicd_metrics`)
* **Kyun kiya:** Hum chahte the ki jab bhi hamara build chale, toh uska record (jaise build pass hua ya fail, kitna time laga) ek database mein save ho jaye. Iske liye humne Google Cloud ka data warehouse **BigQuery** use kiya.
* **Region fix:** Kyunki hamara Cloud Run service Mumbai (`asia-south1`) mein tha, isiliye BigQuery ka dataset bhi exactly usi location (`asia-south1`) par banana pada, warna location mismatch ka error aa raha tha.

### Step 3: BigQuery Table Banana (`build_logs`)
* **Kyun kiya:** Dataset sirf ek folder ki tarah hota hai. Uske andar data store karne ke liye ek table chahiye hoti hai. Isiliye humne `build_logs` naam ki table banai jisme `build_id`, `status`, `build_time`, aur `duration` jaisi fields save hongi.

### Step 4: IAM & Permissions Set Karna (Sabse Important!)
* **Kyun kiya:** Jab Cloud Build ka step BigQuery mein data insert karne ki koshish karta hai, toh Google Cloud poochta hai ki *"Kya is computer/service ke paas BigQuery use karne ki permission hai?"* 
* Pehle permission nahi thi, isiliye **"Access Denied"** ka error aa raha tha.
* **Humne kya kiya:** 
  1. Google Cloud Console mein **IAM & Admin** par gaye.
  2. Apne project ke default service account (`803434570059-compute@developer.gserviceaccount.com`) ko roles diye:
     * **BigQuery Data Editor:** Table ke andar data likhne (insert) karne ke liye.
     * **BigQuery Job User:** BigQuery mein queries run karne ke liye.
* In permissions ke milte hi Cloud Build bina kisi rok-tok ke BigQuery mein logs save karne laga!

---

## 3. Sabse Kaam Ki Commands (Quick Reference)

Agar aapko kabhi bhi dobara sab kuch check karna ho, toh yeh commands use karein:

1. **Build Run Karne Ke Liye:**
   ```bash
   gcloud builds submit --config cloudbuild.yaml .

2. bq logs chekc krne ke liye

bq --location=asia-south1 query --use_legacy_sql=false \
"SELECT status, COUNT(*) as count FROM \`project-fff88c03-dbb0-49b5-994.cicd_metrics.build_logs\` GROUP BY status"


