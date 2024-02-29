def agregar_info_canal():
    nombre_canal = input("Nombre del canal: ")
    genero = input("Género: ")
    logo = input("URL del logo del canal: ")
    url_canal = input("URL del canal: ")
    
    print("\nConfirmar información:")
    print(f"Nombre del canal: {nombre_canal}")
    print(f"Género: {genero}")
    print(f"URL del logo del canal: {logo}")
    print(f"URL del canal: {url_canal}")
    
    confirmacion = input("\n¿Está seguro de que desea agregar esta información? (s/n): ")
    if confirmacion.lower() == 's':
        with open("channel_info.txt", "a") as archivo:
            archivo.write(f"{nombre_canal} | {genero} | {logo} | \n{url_canal}\n")
        print("La información se ha agregado correctamente al archivo.")
    else:
        print("La información no se ha agregado al archivo.")

while True:
    agregar_info_canal()
    respuesta = input("\n¿Deseas agregar otro canal? (s/n): ")
    if respuesta.lower() != 's':
        break
