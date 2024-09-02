import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import random
import time
import json
import os

class VirtualPet:
    def __init__(self, name="Fluffy", env_size=(10, 10)):
        self.name = name
        self.happiness = 100
        self.hunger = 100
        self.energy = 100
        self.position = [env_size[0] // 2, env_size[1] // 2]  # Start in the middle of the environment
        self.env_size = env_size
        self.last_play_time = time.time()  # Record the time of the last play

    def feed(self, amount):
        self.hunger = min(self.hunger + amount, 100)
        self.happiness = min(self.happiness + amount * 0.5, 100)  # Increase happiness with feeding
        self.update_happiness()

    def play(self, time_played):
        if self.energy <= 0:
            return f"{self.name} is too tired to play."

        energy_decrease = time_played + (100 - self.hunger) * 0.1  # Increased energy cost if hungrier
        self.happiness = min(self.happiness + time_played * 0.5, 100)  # Increase happiness with play
        self.energy = max(self.energy - energy_decrease, 0)
        self.hunger = max(self.hunger - (time_played * 2), 0)  # Hunger decreases more with play
        self.last_play_time = time.time()
        self.update_happiness()

    def rest(self, time_rest):
        self.energy = min(self.energy + time_rest, 100)
        self.happiness = min(self.happiness + time_rest * 0.3, 100)  # Increase happiness with rest
        self.update_happiness()

    def decrease_hunger_over_time(self):
        self.hunger = max(self.hunger - 0.1, 0)  # Gradual decrease in hunger over time

    def decrease_energy_over_time(self):
        self.energy = max(self.energy - 0.1, 0)  # Gradual decrease in energy over time

    def update_happiness(self):
        # Decrease happiness based on hunger, energy, and time since last play
        hunger_penalty = (100 - self.hunger) * 0.2
        energy_penalty = (100 - self.energy) * 0.2
        time_since_last_play = time.time() - self.last_play_time
        time_penalty = min(time_since_last_play // 10, 20)  # max penalty capped to 20

        # Increase happiness based on recent play
        recent_play_boost = min((time.time() - self.last_play_time) * 0.1, 20)  # Boost capped to 20

        total_penalty = hunger_penalty + energy_penalty + time_penalty
        self.happiness = max(self.happiness - total_penalty + recent_play_boost, 0)

    def move(self):
        if self.energy <= 0:
            return  # The pet is not active if there's no energy
        
        direction = random.choice(['up', 'down', 'left', 'right'])
        if direction == 'up' and self.position[1] > 0:
            self.position[1] -= 1
        elif direction == 'down' and self.position[1] < self.env_size[1] - 1:
            self.position[1] += 1
        elif direction == 'left' and self.position[0] > 0:
            self.position[0] -= 1
        elif direction == 'right' and self.position[0] < self.env_size[0] - 1:
            self.position[0] += 1

    def get_status(self):
        return f"{self.name}'s Status:\nHappiness: {int(self.happiness)}\nHunger: {int(self.hunger)}\nEnergy: {int(self.energy)}\nPosition: {self.position}"

    def get_mood(self):
        if self.happiness < 30:
            return "sad"
        elif self.happiness < 70:
            return "okay"
        return "happy"

    def to_dict(self):
        return {
            "name": self.name,
            "happiness": self.happiness,
            "hunger": self.hunger,
            "energy": self.energy,
            "position": self.position,
            "last_play_time": self.last_play_time
        }

    def from_dict(self, data):
        self.name = data.get("name", "Fluffy")
        self.happiness = data.get("happiness", 100)
        self.hunger = data.get("hunger", 100)
        self.energy = data.get("energy", 100)
        self.position = data.get("position", [self.env_size[0] // 2, self.env_size[1] // 2])
        self.last_play_time = data.get("last_play_time", time.time())

class PetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Pet App")

        self.pet = self.load_pet_data()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        # Main tab
        self.main_frame = tk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main")

        self.name_label = tk.Label(self.main_frame, text=f"Your Pet: {self.pet.name}", font=("Arial", 16))
        self.name_label.pack(pady=5)

        self.status_label = tk.Label(self.main_frame, text=self.pet.get_status(), padx=10, pady=10)
        self.status_label.pack()

        self.env_canvas = tk.Canvas(self.main_frame, width=300, height=300, bg="white")
        self.env_canvas.pack()

        self.feed_button = tk.Button(self.main_frame, text="Feed Pet", command=self.feed_pet)
        self.feed_button.pack(pady=5)

        self.play_button = tk.Button(self.main_frame, text="Play with Pet", command=self.play_with_pet)
        self.play_button.pack(pady=5)

        self.rest_button = tk.Button(self.main_frame, text="Rest Pet", command=self.rest_pet)
        self.rest_button.pack(pady=5)

        self.customize_button = tk.Button(self.main_frame, text="Customize Pet", command=self.customize_pet)
        self.customize_button.pack(pady=5)

        # Statistics tab
        self.stats_frame = tk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")

        self.stats_label = tk.Label(self.stats_frame, text=self.get_stats(), padx=10, pady=10, justify="left")
        self.stats_label.pack()

        self.update_pet()

    def draw_environment(self):
        self.env_canvas.delete("all")  # Clear the canvas

        cell_size = 30
        for i in range(self.pet.env_size[0]):
            for j in range(self.pet.env_size[1]):
                x1, y1 = i * cell_size, j * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                self.env_canvas.create_rectangle(x1, y1, x2, y2, outline="black")

        # Draw the pet at its current position
        pet_x1 = self.pet.position[0] * cell_size
        pet_y1 = self.pet.position[1] * cell_size
        pet_x2 = pet_x1 + cell_size
        pet_y2 = pet_y1 + cell_size
        self.env_canvas.create_oval(pet_x1, pet_y1, pet_x2, pet_y2, fill="yellow")

    def update_status(self):
        self.status_label.config(text=self.pet.get_status())
        self.stats_label.config(text=self.get_stats())
        self.draw_environment()

    def feed_pet(self):
        self.pet.feed(20)
        self.save_pet_data()
        self.update_status()

    def play_with_pet(self):
        message = self.pet.play(20)
        if message:
            messagebox.showinfo("Play", message)
        self.save_pet_data()
        self.update_status()

    def rest_pet(self):
        self.pet.rest(30)
        self.save_pet_data()
        self.update_status()

    def customize_pet(self):
        new_name = simpledialog.askstring("Customize Pet", "Enter your pet's new name:")
        if new_name:
            self.pet.name = new_name
            self.name_label.config(text=f"Your Pet: {self.pet.name}")
            self.save_pet_data()
            self.update_status()

    def update_pet(self):
        self.pet.move()  # Move the pet in the environment
        self.pet.decrease_hunger_over_time()  # Gradual decrease in hunger
        self.pet.decrease_energy_over_time()  # Gradual decrease in energy
        self.pet.update_happiness()  # Update happiness based on new conditions
        self.update_status()

        # Continue to update the pet's state and environment every second
        self.root.after(1000, self.update_pet)

    def get_stats(self):
        return (f"Name: {self.pet.name}\n"
                f"Happiness: {int(self.pet.happiness)}\n"
                f"Hunger: {int(self.pet.hunger)}\n"
                f"Energy: {int(self.pet.energy)}\n"
                f"Position: {self.pet.position}\n"
                f"Last Play Time: {time.ctime(self.pet.last_play_time)}")

    def load_pet_data(self):
        if os.path.exists("pet_data.json"):
            with open("pet_data.json", "r") as file:
                data = json.load(file)
                pet = VirtualPet()
                pet.from_dict(data)
                return pet
        else:
            return VirtualPet()

    def save_pet_data(self):
        with open("pet_data.json", "w") as file:
            json.dump(self.pet.to_dict(), file, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = PetApp(root)
    root.mainloop()
