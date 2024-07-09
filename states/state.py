from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    full_name = State()
    phone = State()
    age = State()
    confirmFio = State()
    confirmPhone = State()
    confirmAge = State()
    finishReg = State()


class Record(StatesGroup):
    select_date = State()
    send_request = State()


class MenuState(StatesGroup):
    about = State()
    main = State()
    contact = State()
    profile = State()
    promo = State()
    apointment = State()
    reception_history = State()
    visit_dates = State()
    result_analysis = ()


class Admin(StatesGroup):
    menu = State()

    replace_txt_hi = State()
    confirm_replace_txt_hi = State()

    edit_promo_menu = State()

    delete_promo = State()
    get_promo_name = State()
    get_confirm_name_del = State()

    add_promo = State()
    set_promo_name = State()
    confirm_promo_name = State()
    set_promo_desc = State()
    confirm_promo_desc = State()
    is_need_url = State()
    confirm_url_no = State()
    send_url = State()
    confirm_promo_send_url = State()

    create_mailling = State()
    confirm_mailling_name = State()
    input_mailling_desc = State()
    confirm_mailling_desc = State()
    is_need_btn = State()
    input_text_btn = State()
    confirm_input_text_btn = State()
    input_url_btn = State()
    confirm_input_url_btn = State()
