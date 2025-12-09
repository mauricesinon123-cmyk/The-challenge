from PythonProject import create_app

#Creeërt de flask applicatie
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

