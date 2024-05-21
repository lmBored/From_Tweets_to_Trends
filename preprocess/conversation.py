import timeit
import logging
import sys
import datetime

airlines = {"KLM": 56377143 ,
            "AirFrance": 106062176 ,
            "British_Airways": 18332190 ,
            "AmericanAir": 22536055 ,
            "Lufthansa": 124476322 ,
            "AirBerlin": 26223583 ,
            "AirBerlin assist": 2182373406 ,
            "easyJet": 38676903 ,
            "RyanAir": 1542862735 ,
            "SingaporeAir": 253340062 ,
            "Qantas": 218730857 ,
            "EtihadAirways": 45621423 ,
            "VirginAtlantic": 20626359
            }

def conversation_clear(connection):
    connection.cursor().execute("DELETE FROM `hasher`")
    connection.cursor().execute("DELETE FROM `conversations`")
    print("Done!")

def conversation_adder(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY timestamp_ms DESC")
    tweets = cursor.fetchall()
    print("Done fetching tweets!")
    
    n = len(tweets)

    member_of = {}
    conv_id = 1
    run = 0
    
    elapsed = 0
    counter = 0

    for t in tweets:
        errors = 0
        print(f"📍 Processing: {t[0]}")
        start = timeit.default_timer()
        
        tweet = t[0]
        reply_id = t[2]
        tstamp = t[4]
        user_id = t[6]
        
        if tweet in member_of:
            convs = member_of.pop(tweet)
            for conv in convs:
                cursor.execute(f"SELECT * FROM `conversations` WHERE conversation_id={conv}")
                conv_info=cursor.fetchall()
                conv_airline = conv_info[0][3]
                length = 1 + conv_info[0][4]          
                cursor.execute(f"INSERT INTO `hasher`(id,conversation_id) VALUES ({tweet},{conv})")
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
            convs=[conv_id]
            if reply_id != 0:
                if user_id in airlines:
                    cursor.execute(f"""INSERT INTO `conversations`(conversation_id,start, end, airline, length)
                    VALUES ({conv_id}, {tstamp}, {tstamp}, '[{airlines[user_id]}]', 1)""")
                else:
                    cursor.execute(f"""INSERT INTO `conversations`(conversation_id,start, end, length)
                    VALUES ({conv_id}, {tstamp}, {tstamp}, 1)""")
                cursor.execute(f"INSERT INTO `hasher`(id,conversation_id) VALUES ({tweet},{conv_id})") 
                conv_id += 1
        
        if reply_id != 0:
            if reply_id in member_of:
                member_of[reply_id] = member_of[reply_id] + convs 
            else:
                member_of[reply_id] = convs
                
        if run % round(n/10) == 0:
            try:
                connection.commit()
            except Exception as e:
                logging.error(f"Error: {e}, Tweet: {tweet}")
                errors += 1
        run += 1
        
        duration = timeit.default_timer() - start
        if errors == 0:
                print(f"✅ {tweet} appended.")
        else:
            print(f"❌ {tweet} not appended processed - {errors} exceptions ignored.", file=sys.stderr)
        counter += 1
        elapsed += duration
        time_remaining = (n - counter) * (elapsed / counter)
        print(f"⏯️ Process: {(counter/n)*100:.2f}% - #️⃣ {counter}/{n} files processed - ⏳ Time remaining : {str(datetime.timedelta(seconds=time_remaining))}")
        print("-----------------------------------")    