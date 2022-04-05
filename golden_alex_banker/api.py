from requests import post,get
import simplejson as json
import hashlib

from telethon.client import auth

def auth_agent(login,password):
    data = {
        "login": login,
        "password": password
    }
    response = post("http://api.superplat.pw/api/v1/auth", data=json.dumps(data)).json()
    print(response['token'])

    return response['token']

auth_alex777_sub = auth_agent("Alex777_k","7fe2dbfa9359abf67d9acf9f9f59101e")



def create_terminal(parent_id,login):
    headers = {
        'Content-Type':'application/json','Token': str(auth_alex777_sub)
    }
    data = {
        'parentId' : parent_id,
        'count':1,
        'login':login,
    }
    response = post("http://api.superplat.pw/api/v1/addTerminals", headers=headers, data=json.dumps(data)).json()
    print(response)
    
    return response
    
def get_user_balance(user_id):
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777_sub)
    }
    data = {
        'id' : user_id,
    }
    response = post("http://api.superplat.pw/api/v1/getBalanceTerminal", headers=headers, data=json.dumps(data)).json()
    print("Balance: " + str(response))
    return response['amount']


def get_subagnet_balance(user_id,currency_id):
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777_sub)
    }
    data = {
        'id' : user_id,
        'currencyId':currency_id
    }
    response = post("http://api.superplat.pw/api/v1/getBalance", headers=headers, data=json.dumps(data)).json()

    return response['amount']
    

def get_account_info(user_id):
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777_sub)
    }
    data = {
        'id' : user_id,
    }

    response = post("http://api.superplat.pw/api/v1/getInfo", headers=headers, data=json.dumps(data)).json()
    
    return response

def get_terminals(parent_id,filter_by,filter):
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777_sub)
    }
    data = {
        "parentId": parent_id,
        "filterBy": filter_by,
        "filter": filter
    }
    response = post("http://api.superplat.pw/api/v1/getTerminals", headers=headers, data=json.dumps(data)).json()
   
    return response

def get_terminal_link(terminal_id):
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777_sub)
    }
    data = {
        "id": terminal_id,
    }
    response = post("http://api.superplat.pw/api/v1/getTokenLink", headers=headers, data=json.dumps(data)).text
   
    return response

def get_total_transactions(parent_id,terminal_login,from_date,to_date):
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777_sub)
    }
    data = {
        "parentId": parent_id,
        "terminal": terminal_login,
        "from": from_date,
        "to":to_date
    }
    response = post("http://api.superplat.pw/api/v1/getTerminalTransactionsTotal", headers=headers, data=json.dumps(data)).json()

    return response

def terminal_deposit(terminal_login,amount):
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777_sub)
    }
    data = {
        "terminalLogin": terminal_login,
        "isTerminal": True,
        "isDeposit": True,
        "amount":amount
    }
    response = post("http://api.superplat.pw/api/v1/doTransaction", headers=headers, data=json.dumps(data)).json()
    print(response)
    return response

def terminal_deposit_bonus(terminal_login,amount):
    auth_free300 = auth_agent("Free300","46fc0cdc6875e13cfecf3919003a6db0")
    headers = {
        'Content-Type':'application/json','Token':str(auth_free300)
    }
    data = {
        "terminalLogin": terminal_login,
        "isTerminal": True,
        "isDeposit": True,
        "amount":amount
    }
    response = post("http://api.superplat.pw/api/v1/doTransaction", headers=headers, data=json.dumps(data)).json()
    print(response)
    return response


def agent_deposit_subagent(user_id,amount):
    auth_alex777 = auth_agent("Alex777","f513045c8c540ab3b453b700d494666b")
    print("Agent Token: " + str(auth_alex777))
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777)
    }
    data = {
        "remoteId": user_id,
        "isTerminal": False,
        "isDeposit": True,
        "amount":amount
    }
    response = post("http://api.superplat.pw/api/v1/doTransaction", headers=headers, data=json.dumps(data)).json()
    print(response)
    return response

def terminal_collect(terminal_id):
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777_sub)
    }
    data = {
        "id": terminal_id
    }
    response = post("http://api.superplat.pw/api/v1/collectTerminal", headers=headers, data=json.dumps(data)).json()

    return response

def get_terminal_transactions(parentId,terminal,count,from_date,to_date):
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777_sub)
    }
    data = {
        "parentId": parentId,
        "terminal": terminal,
        "count": count,
        "from": from_date,
        "to":to_date
    }
    response = post("http://api.superplat.pw/api/v1/getTerminalTransactions", headers=headers, data=json.dumps(data)).json()

    return response

def get_terminal_bets_info(terminal_id,from_date,to_date):
    headers = {
        'Content-Type':'application/json','Token':str(auth_alex777_sub)
    }
    data = {
        "id": terminal_id,
        "from": from_date,
        "to":to_date
    }
    response = post("http://api.superplat.pw/api/v1/getTerminalLog", headers=headers, data=json.dumps(data)).json()

    return response