# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flaskext.mysql import MySQL
import pymysql

app = Flask(__name__)
app.secret_key = "balkac15"

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '3440536*'
app.config['MYSQL_DATABASE_DB'] = 'songs_of_all_time'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def Index():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("""
    SELECT  
    s.song_id,
	s.song_name AS songname,
    p.producertag AS producer,
    a.artistname AS artist,
    m.artist_name AS mixartist,
    s.song_scale,
    s.duration,
    s.genre,
    s.release_year,
    al.album_name AS albumname 
    FROM songs s
    JOIN producers p
        ON s.producer_id = p.producer_id
    JOIN artists a
        ON s.artist_id = a.artist_id
    JOIN mixartists m
        ON s.mix_artist_id = m.mix_artist_id
    LEFT JOIN albums al
        ON s.album_id = al.album_id
 
    """)

    data = cur.fetchall()

    #ARTIST INFORMATION
    cur.execute("""
    SELECT a.artistname, u.firstname ,u.lastname, a.is_indie, count(s.artist_id) as songsnumber
        from artists a
        LEFT JOIN songs s ON a.artist_id = s.artist_id
        JOIN users u ON a.user_id = u.user_id
        GROUP BY a.artistname
    """)

    data2 = cur.fetchall()

    cur.execute("""
    SELECT p.producertag, u.firstname ,u.lastname, p.labelname, count(s.producer_id) as songsnumber
        from producers p
        LEFT JOIN songs s ON p.producer_id= s.producer_id
        JOIN users u ON p.user_id = u.user_id
        GROUP BY p.producertag
    """)

    data3 = cur.fetchall()

    cur.execute("""
    SELECT m.artist_name, u.firstname ,u.lastname, m.is_simple_mixer, count(s.mix_artist_id) as songsnumber
        from mixartists m
        LEFT JOIN songs s ON m.mix_artist_id= s.mix_artist_id
        JOIN users u ON m.user_id = u.user_id
        GROUP BY m.artist_name
    
    """)

    data4 = cur.fetchall()

    cur.execute("""
        SELECT  artist_id,artistname
        From artists 
    """)

    data5= cur.fetchall()

    cur.execute("""
           SELECT  producer_id,producertag
           From producers
       """)

    data6 = cur.fetchall()

    cur.execute("""
           SELECT  mix_artist_id,artist_name
           From mixartists 
       """)

    data7 = cur.fetchall()

    cur.execute("""
               SELECT  album_id,album_name
               From albums 
           """)

    data8 = cur.fetchall()

    cur.close()

    return render_template('index.html',songs = data ,artists = data2 , producers =data3 ,mixers = data4, artistlist = data5 , producerlist = data6, mixerlist = data7, albumlist = data8)

@app.route('/add_song', methods=['POST'])
def add_song():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        songsname = request.form['songsname']

        #FINDING PRODUCER_ID FROM PRODUCERTAG
        producer_name = request.form['producer']
        cur.execute("""
        SELECT * FROM producers WHERE producertag = %s
        """ , (producer_name))
        producer = cur.fetchone() #Fetch one record and return result
        producerid = producer['producer_id']

        # FINDING ARTIST_ID FROM ARTISTNAME
        artist_name = request.form['artistname']
        cur.execute("""
        SELECT * FROM artists WHERE artistname = %s
        """, (artist_name))
        artist = cur.fetchone()
        artistid = artist['artist_id']

        # FINDING MIX_ID FROM ARTISTNAME
        mix_name = request.form['mixartistname']
        cur.execute("""
        SELECT * FROM mixartists WHERE artist_name = %s
        """,(mix_name))
        mixartist = cur.fetchone()
        mixid = mixartist['mix_artist_id']

        album_name = request.form['albumname']
        if (album_name == '-'):
            albumid = None
        else:
            # FINDING ALBUM_ID FROM ARTISTNAME
            cur.execute("""
            SELECT * FROM albums WHERE album_name = %s 
            """ , (album_name))
            album = cur.fetchone()
            albumid = album['album_id']

        songscale = request.form['songscale']
        duration = request.form['duration']
        genre = request.form['genre']
        releaseyear = request.form['releaseyear']

        cur.execute("""INSERT INTO songs(song_name, producer_id, artist_id, mix_artist_id, 
        song_scale, duration, genre, release_year, album_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (songsname, producerid, artistid, mixid, songscale, duration, genre, releaseyear, albumid))
        conn.commit()
        flash('Song Added Successfully')
        return redirect(url_for(('Index')))

@app.route('/edit/<id>', methods =['POST' , 'GET'])
def get_song(id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute(""" 
    SELECT  
    s.song_id,
	s.song_name AS songname,
    p.producertag AS producer,
    a.artistname AS artist,
    m.artist_name AS mixartist,
    s.song_scale,
    s.duration,
    s.genre,
    s.release_year,
    al.album_name AS albumname 
    FROM songs s
    JOIN producers p
        ON s.producer_id = p.producer_id
    JOIN artists a
        ON s.artist_id = a.artist_id
    JOIN mixartists m
        ON s.mix_artist_id = m.mix_artist_id
    LEFT JOIN albums al
        ON s.album_id = al.album_id
    WHERE s.song_id = %s
    """, {id})
    data= cur.fetchall()
    cur.close()
    return render_template('edit.html',song = data[0])

@app.route('/update/<id>' , methods=['POST'])
def update_song(id):
    songscale = request.form['songscale']
    genre = request.form['genre']
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""UPDATE songs SET song_scale=%s, genre=%s WHERE song_id =%s """, (songscale, genre, id ))
    flash('Song Updated Successfully') #you can change only scale and genre
    conn.commit()
    return redirect(url_for('Index'))

@app.route('/delete/<id>' , methods= ['POST','GET'])
def delete_song(id):
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute('DELETE FROM songs WHERE song_id = %s', {id})
    conn.commit()
    flash('Song Deleted Successfully')
    return redirect(url_for('Index'))

@app.route('/adduser' , methods=['POST' , 'GET'])
def add_user():
    return render_template('adduser.html')

@app.route('/addusercomplete', methods=['POST'])
def add_user_complete():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    phonenumber = request.form['phonenumber']
    age = request.form['age']
    print(firstname + lastname + email + phonenumber +age)
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""INSERT INTO users(firstname,lastname,email,phonenumber,age) VALUES(%s,%s,%s,%s,%s) """,
                (firstname,lastname,email,phonenumber,age))
    conn.commit()
    flash('User Added Successfully.')
    return redirect(url_for('Index'))

@app.route('/addproducer',methods=['POST', 'GET'])
def add_producer():
    return render_template('addproducer.html')

@app.route('/addproducercomplete', methods=['POST'])
def add_producer_complete():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    producertag = request.form['producertag']
    # FINDING USER_ID FROM EMAIL
    producer_mail = request.form['producermail']
    cur.execute("""
            SELECT * FROM users WHERE email = %s
            """, (producer_mail))
    user = cur.fetchone()
    userid = user['user_id']
    labelname = request.form['labelname']

    cur.execute("""
    INSERT INTO producers(user_id,producertag,labelname) VALUES(%s,%s,%s) 
    """,(userid,producertag,labelname))
    conn.commit()
    flash('Producer Added Successfully.')
    return redirect(url_for('Index'))

@app.route('/addartist',methods=['POST', 'GET'])
def add_artist():
    return render_template('addartist.html')

@app.route('/addartistcomplete' , methods = ['POST'])
def add_artist_complete():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    artistname = request.form['artistname']
    artist_mail =request.form['artistmail']
    cur.execute("""
    SELECT * FROM users WHERE email = %s
    """, (artist_mail))
    user = cur.fetchone()
    userid = user['user_id']
    true_or_false = request.form['isindie']
    isindie = False
    if true_or_false == 'yes':
        isindie = True
    cur.execute("""
        INSERT INTO artists(user_id,artistname,is_indie) VALUES(%s,%s,%s) 
    """, (userid,artistname,isindie))
    conn.commit()
    flash('Artist Added Successfully.')
    return redirect(url_for('Index'))

@app.route('/addmixartist', methods=['POST', 'GET'])
def add_mix_artist():
    return render_template('addmixartist.html')

@app.route('/addmixartistcomplete' , methods= ['POST'])
def add_mix_artist_complete():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    mix_artist_name = request.form['mixartistname']
    mix_artist_mail = request.form['mixartistmail']
    cur.execute("""
        SELECT * FROM users WHERE email = %s
        """, (mix_artist_mail))
    user = cur.fetchone()
    userid = user['user_id']
    true_or_false = request.form['issimple']
    is_simple = False
    if true_or_false == 'yes':
        is_simple = True
    cur.execute("""
            INSERT INTO mixartists(user_id,artist_name,is_simple_mixer) VALUES(%s,%s,%s) 
        """, (userid, mix_artist_name , is_simple))
    conn.commit()
    flash('Mix Artist Added Successfully.')
    return redirect(url_for('Index'))

@app.route('/addalbum', methods= ['POST', 'GET'])
def add_album():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("""
           SELECT  artistname
           From artists 
       """)  # to send to artistlist
    data = cur.fetchall()

    return render_template('addalbum.html' , artistlist = data)

@app.route('/addalbumcomplete' , methods= ['POST'])
def add_album_complete():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    album_name = request.form['albumname']

    artist_name = request.form['artistname']
    cur.execute("""
          SELECT * FROM artists WHERE artistname = %s
    """, (artist_name)) # to fetch artistname to id in artists table
    artist = cur.fetchone()

    artist_id = artist['artist_id']
    album_year = request.form['albumyear']
    cur.execute("""
               INSERT INTO albums(album_name,artist_id,release_year) VALUES(%s,%s,%s) 
           """, (album_name,artist_id,album_year))
    conn.commit()
    flash('Album Added Successfully.')
    return redirect(url_for('Index'))