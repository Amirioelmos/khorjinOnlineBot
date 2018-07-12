
"""Simple Bot to Reply to Bale messages."""
import asyncio
import datetime
#import requests

import time
from balebot.filters import TextFilter
from balebot.models.messages import *
from balebot.updater import Updater
from balebot.handlers import *
from balebot.filters import *
from balebot.models.messages.banking.money_request_type import MoneyRequestType
from balebot.filters.bank_message_filter import BankMessageFilter
from balebot.models.base_models import Peer
import pymysql
from balebot.models.messages.banking import money_request_type


user = {"name" : "null", "phone" : "09", "address" :""}
cart = {"peste": 0, "kolompe" : 0, "zire":0, "govato":0 }


peste_fi = 33
zire_fi = 100
kolompe_fi = 30
govato_fi = 40
registerFlag = False





updater = Updater(token="***********************************",loop=asyncio.get_event_loop())




# Define dispatcher
dispatcher = updater.dispatcher
final_cash_2 = 0


def updateFies():
    global peste_fi
    global zire_fi
    global kolompe_fi
    global govato_fi
    mydb = con()
    cursor = mydb.cursor()
    fi_query = 'select price from good where good_id={}'.format(1)
    cursor.execute(fi_query)
    fi = cursor.fetchone()
    peste_fi = fi['price']

    fi_query = 'select price from good where good_id={}'.format(2)
    cursor.execute(fi_query)
    fi = cursor.fetchone()
    zire_fi = fi['price']

    fi_query = 'select price from good where good_id={}'.format(3)
    cursor.execute(fi_query)
    fi = cursor.fetchone()
    kolompe_fi = fi['price']

    fi_query = 'select price from good where good_id={}'.format(3)
    cursor.execute(fi_query)
    fi = cursor.fetchone()
    govato_fi = fi['price']
    cursor.close()

def loadUser(peer_id):

    mydb = con()
    cursor = mydb.cursor()
    user_query = 'select name,phone,address from user where peer_id={}'.format(peer_id)
    cursor.execute(user_query)
    fetched_user = cursor.fetchone()
    user.update({"name": fetched_user['name']})
    user.update({"address": fetched_user['address']})
    user.update({"phone": fetched_user['phone']})
    print("user loaded")
    print(user)
    cursor.close()


def con():
    return pymysql.connect(host='localhost',
                           user='root',
                           password='*****',  
                           db='khorjin',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)

def success(response, user_data):
    print("success : ", response)
    print(user_data)

def failure(response, user_data):
    print("failure : ", response)
    print(user_data)

def successRequest(response, user_data):
    print("user_data=>")
    print(user_data)
    user_data = user_data['kwargs']
    user_peer = user_data["user_peer"]
    bot = user_data["bot"]
    peer = Peer(peer_type="Group",peer_id=1969579684, access_hash="6843459081900717134")
    msg = """
    درخواست جدید:
    قوتو : {0}
    پسته : {1}
    زیره : {2}
   کلمپه : {3}
   -----------------
   توسط : {4}
  به شماره تلفن : {5}
   به ادرس : {6}

    مبلغ : {7}هزار تومان پرداخت شده است. 

    """.format(cart.get("govato"), cart.get("peste"), cart.get("zire"), cart.get("kolompe"), user.get("name"), user.get("phone"), user.get("address"), int(user_data["cash"]) / 10000 )
    message = TextMessage(msg)
    print(message)
    bot.send_message(message, peer)

def successRegister(response, user_data):
    print("user=>")
    print(user)
    user_data = user_data['kwargs']
    user_peer = user_data["user_peer"]
    bot = user_data["bot"]
    nme = str(user.get("name"))

    phne = str(user.get("phone"))
    addr = str(user.get("address"))
    peer = Peer(peer_type="Group", peer_id=1969579684, access_hash="6843459081900717134")
    msg = """
کاربر جدید با نام و نام خانوادگی : {0}\n
شماره تلفن: {1}\n
و ادرس : {2}\n\nثبت شد.
    
    """.format(nme, phne, addr)
    message = TextMessage(msg)
    bot.send_message(message, peer)

# Run the bot!

@dispatcher.command_handler("start")  # filter text the client enter to bot
def start(bot, update):
    user_peer = update.get_effective_user()
    peer_id = user_peer.peer_id
    mydb = con()
    cursor = mydb.cursor()
    welcome_query = 'select peer_id from user where peer_id={}'.format(peer_id)
    res = cursor.execute(welcome_query)
    if res == 0:
        buttons = [
            TemplateMessageButton(text="ثبت نام - ویرایش اطلاعات", value="/Register", action=0),
            TemplateMessageButton(text="ثبت سفارش جدید", value="/Newrequest", action=0),
            TemplateMessageButton(text="نمایش محصولات", value="/ShowGoods", action=0)
        ]
        message = TextMessage(
            "با سلام خدمت شما کاربر گرامی.\nخواهش مند است عملیات مورد نظر را از لیست زیر انتخاب نمایید")
        tem_msg = TemplateMessage(general_message=message, btn_list=buttons)
        user_peer = update.get_effective_user()
        bot.send_message(tem_msg, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.finish_conversation(update)
    else:
        message = TextMessage("شما قبلا ثبت نام کرده اید. برای ثبت سفارش جدید اقدام نمایید و یا میتوانید محصولات را از ویترین ببینید \n برای ویرایش اطلاعات شخصی خود میتوانید دوباره ثبت نام نمایید")
        bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
        dispatcher.finish_conversation(update)


@dispatcher.command_handler(["/Register"])
@dispatcher.message_handler(filters=TemplateResponseFilter(keywords="Register"))
def new_user_step1(bot, update):
    user_peer = update.get_effective_user()
    print("new user =>")
    print(user_peer.peer_id)
    print(user_peer.access_hash)
    msg = "ضمن عرض خوش آمد به خورجین انلاین خواهش مند است نام و نام خانوادگی خود را وارد نمایید."
    textMsg = TextMessage(msg)
    bot.send_message(textMsg, user_peer,success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), new_user_step2)])

def new_user_step2(bot, update):
    name = update.get_effective_message().text
    user.update({"name": name})
    msg = "نام و نام خانوادی *{}* برای شما ثبت شد. \nشماره تلفن خود را وارد نمایید. عوامل خورجین انلاین از این شماره برای پیگیری سفارش شما استفاده خواهند کرد.".format(name)
    textMsg = TextMessage(msg)
    bot.send_message(textMsg, update.get_effective_user(),success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update,[MessageHandler(TextFilter(), new_user_step3)])

def new_user_step3(bot, update):
    phone = update.get_effective_message().text
    user.update({"phone": phone})
    msg = "شماره تلفن *{}* برای شما ثبت شد.\n برای تحویل سفارش خود ادرس مورد نظر همراه با ادرس پستی را وارد نمایید.".format(phone)
    textMsg = TextMessage(msg)
    bot.send_message(textMsg, update.get_effective_user(), success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), new_user_step4)])

def new_user_step4(bot, update):
    address = update.get_effective_message().text
    user.update({"address": address})
    msg = "ادرس زیر برای شما ثبت شد.\n {} \n ثبت نام شما با موفقیت به اتمام رسید. \n برای ویرایش اطلاعات دوباره ثبت نام نمایید.".format(address)
    textMsg = TextMessage(msg)
    kwargs = {"user_peer": update.get_effective_user(), "bot": bot}
    bot.send_message(textMsg, update.get_effective_user(), success_callback=successRegister, failure_callback=failure, kwargs=kwargs)
    global registerFlag
    registerFlag = True
    mydb = con()
    cursor = mydb.cursor()
    cursor.execute('select MAX(user_id) from user')
    max_id = cursor.fetchall()[0].get("MAX(user_id)")
    print("max_id:")
    print(max_id)
    mydb.close()

    user_peer = update.get_effective_user()
    mydb = con()
    cursor = mydb.cursor()
    insert_query = 'INSERT INTO user(user_id,name,phone,address,peer_id,access_hash) VALUES ({0},\'{1}\',\'{2}\',\'{3}\',{4},\'{5}\')'.format(max_id+1,user.get("name"),user.get("phone"),user.get("address"),user_peer.peer_id,user_peer.access_hash)
    print("insert_query")
    print(insert_query)
    cursor.execute(insert_query)
    mydb.commit()
    mydb.close()
    dispatcher.finish_conversation(update)


@dispatcher.command_handler(["/Newrequest"])
@dispatcher.message_handler(filters=TemplateResponseFilter(keywords="Newrequest"))
def newReq(bot, update):
    user_peer = update.get_effective_user()
    peer_id = user_peer.peer_id
    updateFies()
    global registerFlag
    registerFlag = False
    mydb = con()
    cursor = mydb.cursor()
    welcome_query = 'select peer_id from user where peer_id={}'.format(peer_id)
    res = cursor.execute(welcome_query)
    if res == 1:
        loadUser(peer_id)
        registerFlag = True
    if registerFlag == False:
        msg = "مراحل ثبت نام شما تکمیل نشده است. خواهشمند است ابتدا ثبت نام نمایید."
        textMsg = TextMessage(msg)
        bot.send_message(textMsg, user_peer, success_callback=success, failure_callback=failure)
        new_user_step1()

    bottons = [
        TemplateMessageButton(text="پسته",                          value="ثبت سفارش  پسته", action=1),
        TemplateMessageButton(text="قوتو",                          value="ثبت سفارش  قوتو", action=1),
        TemplateMessageButton(text="کلمپه",                         value="ثبت سفارش  کلمپه", action=1),
        TemplateMessageButton(text="زیره",                          value="ثبت سفارش  زیره", action=1),
        TemplateMessageButton(text="مشاهده لیست سفارش",             value="مشاهده سفارش", action=1),
        TemplateMessageButton(text="ارسال سفارش به خورجین انلاین",   value="ارسال سفارش", action=1)
    ]

    message = TextMessage("جنس مورد نظر خود را انتخاب نمایید.\n\n *توجه داشته باشید* قبل از ارسال سفارش بایستی دکمه *مشاهده سفارش* را بزنید.\n\nبرای ویرایش هر مقدار میتوانید همان مقدار را دوباره سفارش دهید")
    tem_msg = TemplateMessage(general_message=message, btn_list=bottons)
    bot.send_message(tem_msg, user_peer,success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=["ثبت سفارش  پسته"]), setPeste),
        MessageHandler(TemplateResponseFilter(keywords=["ثبت سفارش  قوتو"]), setGovato),
        MessageHandler(TemplateResponseFilter(keywords=["ثبت سفارش  کلمپه"]), setKolompe),
        MessageHandler(TemplateResponseFilter(keywords=["ثبت سفارش  زیره"]), setZire),
        MessageHandler(TemplateResponseFilter(keywords=["مشاهده سفارش"]), showCart),
        MessageHandler(TemplateResponseFilter(keywords=["ارسال سفارش"]), exit_newReq)
    ])

def setPeste(bot, update):
    msg = TextMessage("مقدار کیلو گرم پسته را وارد نمایید :")
    bot.send_message(msg, update.get_effective_user() ,success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update,[MessageHandler(TextFilter(), setPesteKilo)])

def setPesteKilo(bot, update):
    kilo = update.get_effective_message().text
    print(int(kilo))
    cart.update({"peste" : int(kilo)})
    msg = TextMessage("مقدار {} کیلو گرم پسته در سبد خرید شما ثبت شد\n برای ویرایش این مقدار دوباره پسته را سفارش دهید".format(kilo))
    bot.send_message(msg, update.get_effective_user(), success_callback=success, failure_callback=failure)
    newReq(bot, update)

def setGovato(bot, update):
    msg = TextMessage("مقدار کیلو گرم قوتو را وارد نمایید :")
    bot.send_message(msg, update.get_effective_user(), success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), setGovatoKilo)])

def setGovatoKilo(bot, update):
    kilo = update.get_effective_message().text
    print(int(kilo))
    cart.update({"govato" : int(kilo)})
    msg = TextMessage("مقدار {} کیلو گرم قوتو در سبد خرید شما ثبت شد\n برای ویرایش این مقدار دوباره قوتو را سفارش دهید".format(kilo))
    bot.send_message(msg, update.get_effective_user(), success_callback=success, failure_callback=failure)
    newReq(bot, update)

def setKolompe(bot, update):
    msg = TextMessage("مقدار کیلو گرم کلمپه را وارد نمایید :")
    bot.send_message(msg, update.get_effective_user(), success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), setKolompeKilo)])

def setKolompeKilo(bot, update):
    kilo = update.get_effective_message().text
    print(int(kilo))
    cart.update({"kolompe" : int(kilo)})
    msg = TextMessage("مقدار {} کیلو گرم کلمپه در سبد خرید شما ثبت شد\n برای ویرایش این مقدار دوباره کلمپه را سفارش دهید".format(kilo))
    bot.send_message(msg, update.get_effective_user(), success_callback=success, failure_callback=failure)
    newReq(bot, update)

def setZire(bot, update):
    msg = TextMessage("مقدار کیلو گرم زیره سیاه را وارد نمایید :\n در حال حاضر فقط زیره سیاه موجود می باشد")
    bot.send_message(msg, update.get_effective_user(), success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(TextFilter(), setZireKilo)])

def setZireKilo(bot, update):
    kilo = update.get_effective_message().text
    print(int(kilo))
    cart.update({"zire": int(kilo)})
    msg = TextMessage("مقدار {} کیلو گرم زیره سیاه در سبد خرید شما ثبت شد\n برای ویرایش این مقدار دوباره زیره سیاه را سفارش دهید".format(kilo))
    bot.send_message(msg, update.get_effective_user(), success_callback=success, failure_callback=failure)
    newReq(bot,update)

showCartFlag = False

def showCart(bot, update):
    peste_kilo = int(cart.get("peste"))
    kolompe_kilo = int(cart.get("kolompe"))
    zire_kilo = int(cart.get("zire"))
    govato_kilo = int(cart.get("govato"))
    final_cash = peste_kilo * peste_fi + zire_kilo * zire_fi + kolompe_kilo * kolompe_fi + govato_kilo * govato_fi
    print(final_cash)
    cart_text = """
                مقدار پسته :     {0} کیلو گرم \n
                مقدار کلمپه :     {1} کیلو گرم \n
                مقدار زیره :     {2} کیلو گرم \n
                مقدار قوتو :     {3} کیلو گرم\n
قیمت نهایی : {4} هزار تومان 
    """.format(peste_kilo,kolompe_kilo,zire_kilo,govato_kilo,final_cash)
    msg = TextMessage(cart_text)
    bot.send_message(msg, update.get_effective_user(), success_callback=success, failure_callback=failure)
    global showCartFlag
    showCartFlag = True
    dispatcher.set_conversation_data(update=update, key="final_cash", value=final_cash)
    newReq(bot, update)

def exit_newReq(bot, update):
    user_peer = update.get_effective_user()
    global showCartFlag
    if showCartFlag == False:
        msg = "برای نهایی کردن سفارش خود ابتدا باید دکمه *مشاهده لیست سفارش* را بزنید.و سپس دکمه *ارسال سفارش به خورجین انلاین* را بزنید."
        textMsg = TextMessage(msg)
        bot.send_message(textMsg, user_peer, success_callback=success, failure_callback=failure)
        showCart()


    ffinal = dispatcher.get_conversation_data(update=update, key="final_cash") * 10000
    print(str(ffinal))

    mydb = con()
    cursor = mydb.cursor()
    cursor.execute('select MAX(cart_id) from cart')
    max_id = cursor.fetchall()[0].get("MAX(cart_id)")
    print("max_id:")
    print(max_id)
    mydb.close()
    cart_id = max_id + 1
    # status :
    # 1 - user show cart 
    # 2 - user payed cart 
    # database :

    mydb = con()
    cursor = mydb.cursor()
    insert_query = 'INSERT INTO cart(cart_id, status, transaction_id, price, peer_id) VALUES ({0},{1},{2},{3},{4})'.format(cart_id, 1, 0, ffinal, user_peer.peer_id)
    print("insert_query")
    print(insert_query)
    cursor.execute(insert_query)
    mydb.commit()
    mydb.close()



    if (cart.get("peste") != 0):
        mydb = con()
        cursor = mydb.cursor()
        insert_query = 'INSERT INTO cart_good(good_id, cart_id,vol) VALUES ({0},{1},{2})'.format(1,cart_id,cart.get("peste"))
        print("insert_query")
        print(insert_query)
        cursor.execute(insert_query)
        mydb.commit()
        mydb.close()

    if (cart.get("zire") != 0):
        mydb = con()
        cursor = mydb.cursor()
        insert_query = 'INSERT INTO cart_good(good_id, cart_id,vol) VALUES ({0},{1},{2})'.format(2,cart_id,cart.get("zire"))
        print("insert_query")
        print(insert_query)
        cursor.execute(insert_query)
        mydb.commit()
        mydb.close()

    if (cart.get("kolompe") != 0):
        mydb = con()
        cursor = mydb.cursor()
        insert_query = 'INSERT INTO cart_good(good_id, cart_id,vol) VALUES ({0},{1},{2})'.format(3,cart_id,cart.get("kolompe"))
        print("insert_query")
        print(insert_query)
        cursor.execute(insert_query)
        mydb.commit()
        mydb.close()

    if (cart.get("govato") != 0):
        mydb = con()
        cursor = mydb.cursor()
        insert_query = 'INSERT INTO cart_good(good_id, cart_id,vol) VALUES ({0},{1},{2})'.format(4,cart_id,cart.get("govato"))
        print("insert_query")
        print(insert_query)
        cursor.execute(insert_query)
        mydb.commit()
        mydb.close()



    def file_upload_success(result, user_data):
        print("upload was successful : ", result)
        print(user_data)
        file_id = str(user_data.get("file_id", None))
        access_hash = str(user_data.get("user_id", None))
        v_message = PhotoMessage(file_id=file_id, access_hash=access_hash, name="Bale", file_size='11337',
                                 mime_type="image/jpeg",
                                 caption_text=TextMessage(text="با تشکر از خرید شما - خورجین انلاین بعد از پرداخت سفارش شما پیگیری خواهد شد."),
                                 file_storage_version=1, thumb=None)

        purchase_message = PurchaseMessage(msg=v_message, account_number="6037991889250159",
                                           amount=str(ffinal), money_request_type=MoneyRequestType.normal)
        

        bot.send_message(purchase_message, user_peer, success_callback=success, failure_callback=failure)

    bot.upload_file(file="./peste.jpeg", file_type="file", success_callback=file_upload_success,
                    failure_callback=failure)

    cart.update({"zire": 0})
    cart.update({"govato": 0})
    cart.update({"peste": 0})
    cart.update({"kolome": 0})

    dispatcher.set_conversation_data(update=update, key="cart_id", value=cart_id)
    dispatcher.register_conversation_next_step_handler(update, [MessageHandler(BankMessageFilter(), payment_done),
                                                                MessageHandler(DefaultFilter(), default_handler)])

    

def payment_done(bot, update):
    message = update.get_effective_message()
    print("message:", message)
    cart_id =  dispatcher.get_conversation_data(update=update, key="cart_id")
    mydb = con()
    cursor = mydb.cursor()
    update_status_query = 'UPDATE cart SET status=2 where cart_id ={}'.format(cart_id)
    print("insert_query")
    print(update_status_query)
    cursor.execute(update_status_query)
    mydb.commit()
    mydb.close()
    final = ffinal = dispatcher.get_conversation_data(update=update, key="final_cash")
    success_payment = TextMessage("پرداخت با موفقیت انجام شد. برای پیگیری سفارش خود به ایدی @amirio پیام دهید.")
    kwargs = {"user_peer": update.get_effective_user(), "bot": bot, "cart": cart, "cash" : final}
    bot.reply(update, success_payment, success_callback=successRequest, failure_callback=failure, kwargs=kwargs)
    dispatcher.finish_conversation(update)

def default_handler(bot, update):
    message = update.get_effective_message().text
    print("message:", message)
    success_payment = TextMessage("پرداخت شما با مشکل مواجه شده است خواهشمند است دوباره سفارش دهید\nخورجین آنلاین")
    bot.reply(update, success_payment, success_callback=success, failure_callback=failure)
    dispatcher.finish_conversation(update)



@dispatcher.command_handler(["/ShowGoods"])
@dispatcher.message_handler(filters=TemplateResponseFilter(keywords="ShowGoods"))
def showGoods(bot, update):
    user_peer = update.get_effective_user()
    updateFies()
    bottons = [
        TemplateMessageButton(text="پسته", value="مشاهده انواع پسته" , action=1),
        TemplateMessageButton(text=" قوتو", value="مشاهده انواع قوتو" , action=1),
        TemplateMessageButton(text=" کلمپه", value="مشاهده انواع کلمپه" , action=1),
        TemplateMessageButton(text="زیره", value="مشاهده انواع زیره" , action=1),
        TemplateMessageButton(text="پایان نمایش لیست محصولات", value="پایان", action=1)
    ]
    message = TextMessage("جنس خود را انتخاب نمایید")
    template_msg1 = TemplateMessage(general_message=message, btn_list=bottons)
    bot.send_message(template_msg1, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.register_conversation_next_step_handler(update,[
        MessageHandler(TemplateResponseFilter(keywords=["مشاهده انواع پسته"]), showPeste),
        MessageHandler(TemplateResponseFilter(keywords=["مشاهده انواع قوتو"]), showGovato),
        MessageHandler(TemplateResponseFilter(keywords=["مشاهده انواع کلمپه"]), showKolompe),
        MessageHandler(TemplateResponseFilter(keywords=["مشاهده انواع زیره"]), showZire),
        MessageHandler(TemplateResponseFilter(keywords=["پایان"]), exit_showGood),
        MessageHandler(DefaultFilter(),showGoods)
    ])

def showPeste(bot, update):
    user_peer = update.get_effective_user()
    run_message = TextMessage(" در حال پردازش ...")
    bot.send_message(run_message, user_peer, success_callback=success, failure_callback=failure)

    def file_upload_success(result, user_data):
        print("upload was successful : ", result)
        print(user_data)
        file_id = str(user_data.get("file_id", None))
        access_hash = str(user_data.get("user_id", None))
        v_message = PhotoMessage(file_id=file_id, access_hash=access_hash, name="Bale", file_size='11337',
                                 mime_type="image/jpeg", caption_text=TextMessage(text="پسته اکبری - قیمت *{}* هزار تومان".format(peste_fi)),
                                 file_storage_version=1, thumb=None)

        bot.send_message(v_message, user_peer, success_callback=success, failure_callback=failure)

    bot.upload_file(file="./peste.jpeg", file_type="file", success_callback=file_upload_success,
                    failure_callback=failure)

def showGovato(bot, update):
    user_peer = update.get_effective_user()

    run_message = TextMessage(" در حال پردازش ...")
    bot.send_message(run_message, user_peer, success_callback=success, failure_callback=failure)

    def file_upload_success(result, user_data):
        print("upload was successful : ", result)
        print(user_data)
        file_id = str(user_data.get("file_id", None))
        access_hash = str(user_data.get("user_id", None))
        v_message = PhotoMessage(file_id=file_id, access_hash=access_hash, name="Bale", file_size='11337',
                                 mime_type="image/jpeg",
                                 caption_text=TextMessage(text="قوتو خشخاشی - قیمت *{}*  هزار تومان".format(govato_fi)),
                                 file_storage_version=1, thumb=None)

        bot.send_message(v_message, user_peer, success_callback=success, failure_callback=failure)

    bot.upload_file(file="./govato.jpeg", file_type="file", success_callback=file_upload_success,
                    failure_callback=failure)

def showKolompe(bot, update):
    user_peer = update.get_effective_user()

    run_message = TextMessage(" در حال پردازش ...")
    bot.send_message(run_message, user_peer, success_callback=success, failure_callback=failure)

    def file_upload_success(result, user_data):
        print("upload was successful : ", result)
        print(user_data)
        file_id = str(user_data.get("file_id", None))
        access_hash = str(user_data.get("user_id", None))
        v_message = PhotoMessage(file_id=file_id, access_hash=access_hash, name="Bale", file_size='11337',
                                 mime_type="image/jpeg",
                                 caption_text=TextMessage(text="کلمپه گردویی با طعم گلاب کاشان - قیمت *{}* هزار تومان".format(kolompe_fi)),
                                 file_storage_version=1, thumb=None)

        bot.send_message(v_message, user_peer, success_callback=success, failure_callback=failure)

    bot.upload_file(file="./kolompe.jpeg", file_type="file", success_callback=file_upload_success,
                    failure_callback=failure)

def showZire(bot,update):

    user_peer = update.get_effective_user()

    run_message = TextMessage(" در حال پردازش ...")
    bot.send_message(run_message, user_peer, success_callback=success, failure_callback=failure)

    def file_upload_success(result, user_data):
        print("upload was successful : ", result)
        print(user_data)
        file_id = str(user_data.get("file_id", None))
        access_hash = str(user_data.get("user_id", None))
        v_message = PhotoMessage(file_id=file_id, access_hash=access_hash, name="Bale", file_size='11337',
                                 mime_type="image/jpeg",
                                 caption_text=TextMessage(text="زیره سیاه - قیمت *{}* هزار تومان".format(zire_fi)),
                                 file_storage_version=1, thumb=None)

        bot.send_message(v_message, user_peer, success_callback=success, failure_callback=failure)

    bot.upload_file(file="./zire.jpeg", file_type="file", success_callback=file_upload_success,
                    failure_callback=failure)

    

def exit_showGood(bot, update):
    message = TextMessage("برای نمایش منو / را وارد نمایید.")
    user_peer = update.get_effective_user()
    bot.send_message(message, user_peer, success_callback=success, failure_callback=failure)
    dispatcher.finish_conversation(update)

updater.run()
