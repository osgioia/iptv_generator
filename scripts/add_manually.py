def add_new_channel():
    name_channel = input("Nombre del canal: ")
    genre = input("Género: ")
    logo = input("URL del logo del canal: ")
    url_channel = input("URL del canal: ")
    
    print("\nConfirmar información:")
    print(f"Nombre del canal: {name_channel}")
    print(f"Género: {genre}")
    print(f"URL del logo del canal: {logo}")
    print(f"URL del canal: {url_channel}")
    
    confirm = input("\n¿Está seguro de que desea agregar esta información? (s/n): ")
    if confirm.lower() == 's':
        with open("channel_info.txt", "a") as file:
            file.write(f"{name_channel} | {genre} | {logo} | \n{url_channel}\n")
        print("La información se ha agregado correctamente al archivo.")
    else:
        print("La información no se ha agregado al archivo.")

while True:
    add_new_channel()
    response = input("\n¿Deseas agregar otro canal? (s/n): ")
    if response.lower() != 's':
        break
