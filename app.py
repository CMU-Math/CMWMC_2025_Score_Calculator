import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

st.set_page_config(layout="wide")

@st.cache_data(ttl=600)
def get_values(spreadsheet_id, range_name): #reading data
  SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
  # creds = service_account.Credentials.from_service_account_file(
  #   "gcp-service-account.json", scopes=SCOPES)

  creds = service_account.Credentials.from_service_account_file(
    st.secrets["GCP-SERVICE-ACCOUNT"], scopes=SCOPES)
  
  try:
    service = build("sheets", "v4", credentials=creds)

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    rows = result.get("values", [])
    print(f"{len(rows)} rows retrieved")
    return result
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

def rank(lst, score): #finding rank of score in lst
  for i in range(len(lst)):
    if(lst[i] <= score):
      return i + 1
  return len(lst)
    
def data_clean(lst): #data preprocessing
  result = []
  for l in lst:
    if(len(l) == 1):
      result.append(float(l[0]))
  return result

def calc_est(ans): #estimathon calculating
  if(ans == 0):
    return 0
  return min(ans/338350, 338350/ans)

###Backend for gathering data

SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]

indiv_scores_res = get_values(SPREADSHEET_ID, "Individual!Z1:Z57")
indiv_scores = data_clean(indiv_scores_res.get("values", []))
indiv_scores.sort(reverse=True)

team_indiv_res = get_values(SPREADSHEET_ID, "Team Overall!C2:C22")
team_indiv_scores = data_clean(team_indiv_res.get("values", []))
team_indiv_scores.sort(reverse=True)

guts_res = get_values(SPREADSHEET_ID, "Team Overall!C2:C22")
guts_scores = data_clean(guts_res.get("values", []))
guts_scores.sort(reverse=True)

relay_res = get_values(SPREADSHEET_ID, "Team Overall!D2:D22")
relay_scores = data_clean(relay_res.get("values", []))
relay_scores.sort(reverse=True)

overall_res = get_values(SPREADSHEET_ID, "Team Overall!H2:H22")
overall_scores = data_clean(overall_res.get("values", []))
overall_scores.sort(reverse=True)

### App Front-end

st.title("CMWMC 2025 Score Calculator")
st.write("**Input your hypothetical score into the input fields to see what place you would have been.**")

st.subheader("Individual Scores")

input_col, spacer, score_col = st.columns([1, 0.1, 1])

with input_col:
  col1, col2 = st.columns(2)
  with col1:
    contestant1 = st.number_input("Input the number of correct answers for Contestant 1", 0, 20, "min", 1)
    contestant2 = st.number_input("Input the number of correct answers for Contestant 2", 0, 20, "min", 1)
    contestant3 = st.number_input("Input the number of correct answers for Contestant 3", 0, 20, "min", 1)
  with col2:
    est1 = st.number_input("Input the estimathon guess for contestant 1")
    est2 = st.number_input("Input the estimathon guess for contestant 2")
    est3 = st.number_input("Input the estimathon guess for contestant 3")

  st.subheader("Guts Scores")

  guts = st.number_input("Input the number of correct answers for your team", 0, 21, "min", 1)

  st.subheader("Relay Scores")

  col1, col2 = st.columns(2)

  with col1:
    relay1 = st.number_input("Input the number of correct answers for Relay 1", 0, 3, "min", 1)
    relay2 = st.number_input("Input the number of correct answers for Relay 2", 0, 3, "min", 1) 
    relay3 = st.number_input("Input the number of correct answers for Relay 3", 0, 3, "min", 1) 
    relay4 = st.number_input("Input the number of correct answers for Relay 4", 0, 3, "min", 1)
  with col2:
    ex_time1 = st.checkbox("Submitted Relay 1 before 6 minutes (Extra Points)")
    ex_time2 = st.checkbox("Submitted Relay 2 before 6 minutes (Extra Points)")
    ex_time3 = st.checkbox("Submitted Relay 3 before 6 minutes (Extra Points)")
    ex_time4 = st.checkbox("Submitted Relay 4 before 6 minutes (Extra Points)")

with score_col:

  col1, col2, col3 = st.columns(3)
  with col1:

    contestant1 += calc_est(est1)
    contestant2 += calc_est(est2)
    contestant3 += calc_est(est3)

    rank1 = rank(indiv_scores, contestant1)
    rank2 = rank(indiv_scores, contestant2)
    rank3 = rank(indiv_scores, contestant3)

    st.subheader("Individual Ranks")
    st.write("Contestant 1: " + str(rank1))
    st.write("Contestant 2: " + str(rank2))
    st.write("Contestant 3: " + str(rank3))

    indiv1, indiv2, indiv3 = sorted([contestant1, contestant2, contestant3], reverse=True)
    team_indiv = ((3 * indiv1) + (2 * indiv2) + indiv3) / 6
    st.write("Team Raw Score: " + str(team_indiv))

    indiv_normal = 100 * team_indiv / max(team_indiv_scores + [team_indiv])
    st.write("Team Score: " + str(indiv_normal))

  with col2:
    st.subheader("Guts Scores")
    st.write("Team Raw Score: " + str(guts))

    guts_normal = 100 * guts / max(guts_scores + [guts])
    st.write("Team Score: " + str(guts_normal))

  with col3:
    st.subheader("Relay Scores")

    relay_key = {0: 0, 1: 1, 2: 3, 3: 6}
    relay_score = relay_key[relay1] + \
                  relay_key[relay2] + \
                  relay_key[relay3] + \
                  relay_key[relay4]
    if(relay1 == 3):
      relay_score += ex_time1 * 2
    if(relay2 == 3):
      relay_score += ex_time2 * 2
    if(relay3 == 3):
      relay_score += ex_time3 * 2
    if(relay4 == 3):
      relay_score += ex_time4 * 2
    
    st.write("Team Raw Score: " + str(relay_score))

    relay_normal = 100 * relay_score / max(relay_scores + [relay_score])
    st.write("Team Score: " + str(relay_normal))
  

  team_normal = indiv_normal + guts_normal + relay_normal
  st.subheader("Team Overall: " + str(team_normal))
  st.subheader("Team Rank: " + str(rank(overall_scores, team_normal)))
