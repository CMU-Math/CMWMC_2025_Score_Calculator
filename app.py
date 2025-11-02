import streamlit as st
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_values(spreadsheet_id, range_name):
  creds, _ = google.auth.default()
  # pylint: disable=maybe-no-member
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

st.set_page_config(layout="wide")

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
    est1 = st.number_input("Input the estimathon guess for contestant 2")
    est1 = st.number_input("Input the estimathon guess for contestant 3")

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
    st.subheader("Individual Scores")
    st.write("Contestant 1: " + str(contestant1))
    st.write("Contestant 2: " + str(contestant2))
    st.write("Contestant 3: " + str(contestant3))

    indiv1, indiv2, indiv3 = sorted([contestant1, contestant2, contestant3], reverse=True)
    team_indiv = ((3 * indiv1) + (2 * indiv2) + indiv3) / 6
    st.write("Team Overall Score: " + str(team_indiv))

  with col2:
    st.subheader("Guts Scores")
    st.write("Team Score: " + str(guts))

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
    
    st.write("Relay Score: " + str(relay_score))