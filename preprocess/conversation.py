import timeit
import logging
import sys
import datetime

logging.basicConfig(filename='tmp/conversation.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

def conversation_clear(connection):
    connection.cursor().execute("DELETE FROM `hasher`")
    connection.cursor().execute("DELETE FROM `conversations`")
    print("Done!")

def conversation_adder(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY timestamp_ms DESC")
    tweets = cursor.fetchall()
    print("Done fetching tweets!")
    
    airlines= {56377143 : 'KLM',
            106062176:'AirFrance',
            18332190:"British_Airways", 
            22536055:"AmericanAir",
            124476322:"Lufthansa",
            26223583:'AirBerlin',
            2182373406:'AirBerlin assist',
            38676903:"easyJet",
            1542862735:"RyanAir",
            253340062:"SingaporeAir",
            218730857:"Qantas",
            45621423:"EtihadAirways",
            20626359:"VirginAtlantic"}
    
    n = len(tweets)

    member_of = {}
    conversation_id = 1    
    elapsed = 0
    counter = 0

    for t in tweets:
        errors = 0
        print(f"📍 Processing tweet: {t[0]}")
        start = timeit.default_timer()
        
        tweet_id = t[0]
        reply_id = t[2]
        tstamp = t[4]
        user_id = t[6]
        
        if tweet_id in member_of:
            convs = member_of.pop(tweet_id)
            for conv in convs:
                cursor.execute(f"SELECT * FROM `conversations` WHERE conversation_id={conv}")
                conv_info=cursor.fetchall()
                conv_airline = conv_info[0][3]
                length = 1 + conv_info[0][4]          
                cursor.execute(f"INSERT INTO `hasher`(id,conversation_id,conversation_rank) VALUES ({tweet_id},{conv},{length})")
                if user_id in airlines:
                    if conv_airline == '0':
                        cursor.execute(f"""UPDATE `conversations` SET start={tstamp}, airline = '[{airlines[user_id]}]',
                        length = {length} WHERE conversation_id={conv}""") 
                    elif f"{airlines[user_id]}" not in conv_airline:
                        conv_airline_new =  conv_airline.replace(']',f",{airlines[user_id]}]")
                        cursor.execute(f"""UPDATE `conversations` SET start={tstamp}, airline = '{conv_airline_new}',
                        length = {length} WHERE conversation_id={conv}""")
                    else:
                        cursor.execute(f"UPDATE `conversations` SET start={tstamp}, length = {length} WHERE conversation_id={conv}")
                else:
                    cursor.execute(f"UPDATE `conversations` SET start={tstamp}, length = {length} WHERE conversation_id={conv}")
        else:
            convs=[conversation_id]
            if reply_id != 0:
                if user_id in airlines:
                    cursor.execute(f"""INSERT INTO `conversations`(conversation_id,start, end, airline, length)
                    VALUES ({conversation_id}, {tstamp}, {tstamp}, '[{airlines[user_id]}]', 1)""")
                else:
                    cursor.execute(f"""INSERT INTO `conversations`(conversation_id,start, end, length)
                    VALUES ({conversation_id}, {tstamp}, {tstamp}, 1)""")
                cursor.execute(f"INSERT INTO `hasher`(id,conversation_id,conversation_rank) VALUES ({tweet_id},{conversation_id},1)") 
                conversation_id += 1
        
        if reply_id != 0:
            if reply_id in member_of:
                member_of[reply_id] = member_of[reply_id] + convs 
            else:
                member_of[reply_id] = convs
                
        if counter % round(n/100) == 0:
            try:
                connection.commit()
            except Exception as e:
                logging.error(f"Error: {e}, tweet_id: {tweet_id}")
                logger.error(e)
                errors += 1
        
        duration = timeit.default_timer() - start
        if errors == 0:
                print(f"✅ Tweet with id {tweet_id} appended.")
        else:
            print(f"❌ {tweet_id} not appended processed - {errors} exceptions ignored.", file=sys.stderr)
        counter += 1
        elapsed += duration
        time_remaining = (n - counter) * (elapsed / counter)
        print(f"⏯️ Process: {(counter/n)*100:.2f}% - #️⃣ {counter}/{n} tweets processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining))}")
        print("-----------------------------------")
    
    print("✅ Done!")
        
	
def normalize(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `conversations`")
    conversations = cursor.fetchall()
    
    counter = 0
    elapsed = 0
    n = len(conversations)
    
    for i in conversations:
        start = timeit.default_timer()
        errors = 0
        
        conversation_id = i[0] 
        length = i[4]
        cursor.execute(f"SELECT * FROM `hasher` WHERE conversation_id = {conversation_id}")
        conversation = cursor.fetchall()
        for tweet in conversation:
            tweet_id = tweet[0]
            rank = tweet[2] - 1
            cursor.execute(f"""UPDATE `hasher` SET conversation_rank = {length - rank} WHERE id = {tweet_id} AND conversation_id = {conversation_id}""")
        if counter % round(n/10) == 0:
            try:
                connection.commit()
            except Exception as e:
                logging.error(f"Error: {e}, Tweet: {tweet}")
                logger.error(e)
                errors += 1
        
        duration = timeit.default_timer() - start
        if errors == 0:
                print(f"✅ {conversation_id} modified.")
        else:
            print(f"❌ {conversation_id} not modified - {errors} exceptions ignored.", file=sys.stderr)
        counter += 1
        elapsed += duration
        time_remaining = (n - counter) * (elapsed / counter)
        print(f"⏯️ Process: {(counter/n)*100:.2f}% - #️⃣ {counter}/{n} tweets processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining))}")
        print("-----------------------------------")
        
    print("✅ Done!")