import speech_recognition as sr
import pyttsx3
import mysql.connector
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="abcdefgh",
    database="cafeteria"
)
cursor = db.cursor()

# Function to speak text
def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# Function to listen to voice input
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        speak("speak now")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"User said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return None

# Function to get item price from database
def get_item_price(item_name):
    cursor.execute("SELECT price FROM items WHERE item_name = %s", (item_name,))
    result = cursor.fetchone()
    return result[0] if result else None

# Function to record sale in database
def record_sale(item_name, quantity, total_price):
    cursor.execute("INSERT INTO sales (item_id, quantity, total_price) VALUES ((SELECT item_id FROM items WHERE item_name = %s), %s, %s)", (item_name, quantity, total_price))
    db.commit()

# Function to calculate daily sales
def calculate_daily_sales():
    cursor.execute("SELECT SUM(total_price) FROM sales WHERE sale_date = CURDATE()")
    result = cursor.fetchone()
    return result[0] if result else 0

# Function to handle voice input
def handle_voice_input():
    speak("The system is now active. Please say the item name and quantity to make a purchase.")
    total_order_price = 0
    while True:
        command = listen()
        if command:
            if command.lower() in ["stop", "no"]:
                speak(f"The total price for your order is {total_order_price} rupees.")
                break
            try:
                items = command.split(",")
                for item in items:
                    item_name, quantity = item.strip().split()
                    quantity = int(quantity)
                    price = get_item_price(item_name)
                    if price:
                        item_total_price = price * quantity
                        total_order_price += item_total_price
                        record_sale(item_name, quantity, item_total_price)
                        speak(f"Added {quantity} {item_name}(s) to the order.")
                    else:
                        speak(f"Item {item_name} not found.")
                speak(f"The current total price for your order is {total_order_price} rupees.")
                speak("Do you want to add anything else?")
            except ValueError:
                speak("Please provide both item names and quantities correctly.")

# Function to display daily sales
def display_daily_sales():
    total_sales = calculate_daily_sales()
    speak(f"The total sales for today are {total_sales} rupees.")
    messagebox.showinfo("Daily Sales", f"The total sales for today are {total_sales} rupees.")

# Create the main window
root = tk.Tk()
root.title("Cafeteria Billing System")
root.geometry("400x200")

# Create GUI elements
title_label = tk.Label(root, text="Cafeteria Billing System", font=("Arial", 16))
title_label.pack(pady=10)

voice_input_button = tk.Button(root, text="Start Voice Input", command=handle_voice_input, font=("Arial", 12))
voice_input_button.pack(pady=10)

daily_sales_button = tk.Button(root, text="Calculate Daily Sales", command=display_daily_sales, font=("Arial", 12))
daily_sales_button.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12))
exit_button.pack(pady=10)

# Run the main loop
root.mainloop()
