from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import mysql.connector


bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/genesymbol', methods=('GET','POST'))
def searchSymbol():
    if request.method == 'POST':
        sym = request.form['query']
        cnx = mysql.connector.connect(user='root', passwd='root', database='geneEd')
        cur = cnx.cursor()
        query = ("SELECT symbol,fullName,locus FROM gene WHERE symbol = '" + sym + "'")
        cur.execute(query)

        for (symbol,name,locus) in cur:
            return render_template('search_results.html', symbol=symbol, fullName=name, location=locus)
        return render_template('no_results.html',symbol=sym)
    else:
        return render_template('search.html')