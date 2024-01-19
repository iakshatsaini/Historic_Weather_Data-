from flask import jsonify
from connection import postgre_sql_connection
import uuid
from datetime import datetime
import json
from werkzeug.security import check_password_hash, generate_password_hash
from passlib.hash import pbkdf2_sha256

def register_user(username, password):
    pg_conn, pg_cursur = postgre_sql_connection()
    s0 = '''
        select count(*) from public.user where username = '{}'
    '''
    s1 ='''
        INSERT INTO public.user (id, username, password, created_time) VALUES (%s, %s, %s, %s)
        '''
    try:
        if pg_conn and pg_cursur:
            
            pg_cursur.execute(s0.format(username))
            count = pg_cursur.fetchone()[0]
            if count != 0:
                resp = {"message":"user already exist in system, Please try with diffrent username","status":200}
            else:
                uid = uuid.uuid4()
                created_time = datetime.now()
                
                insert_data = (str(uid), username, password, created_time)
                
                pg_cursur.execute(s1, insert_data)
                pg_conn.commit()
                
                resp = {"message":"User registred successfully", "status":200}
        else:
            resp = {"message":"Database connection not establised", "status":403}
        return resp
    except Exception as e:
        return {"message":"Error in registering user", "status":500}
    
    
def user_authentication(username, password):
    pg_conn, pg_cursur = postgre_sql_connection()
    s0 = '''
        select username, password from public.user where username = '{}'
    '''
    resp = {}
    try:
        if pg_conn and pg_cursur:
            
            pg_cursur.execute(s0.format(username))
            userData = pg_cursur.fetchone()
            if userData:
                hashedPassword = userData[1]
                checkHashedPassword = pbkdf2_sha256.verify(password, hashedPassword)
                if checkHashedPassword:
                    resp = {"message":"User logged in successfully!", "status":200, "userName":username}
                else:
                    resp = {"error":"Password is not valid, Please check", "status":401}
            else:
                resp = {"error":"user not found", "status":404}     
        else:
            resp = {"message":"Database connection not establised", "status":403}
        return resp
    except Exception as e:
        return {"message":"Error in authentication", "status":500}