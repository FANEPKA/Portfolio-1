from aiogram.dispatcher.filters.state import State,StatesGroup

class QiwiIn(StatesGroup):
    amount = State()
    
class BtcIn(StatesGroup):
    check = State()    
    

class QiwiOut(StatesGroup):
    amount = State()
    
    
    
class EmailCheck(StatesGroup):
    email = State()
    user_confirm_code = State()
    confirm_code = State()
    