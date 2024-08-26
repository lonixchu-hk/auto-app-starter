# 🚀 Auto App Starter

**Auto App Starter** is a utility tool that helps you memorize the position of your applications across multiple displays and automatically launches them in their saved positions when your PC boots. This tool is ideal for users who work with multi-monitor setups and want a seamless start to their day by having their workspace set up automatically.

## ✨ Features

- 📌 **Memorize Window Positions**: Save the position and size of any open application across multiple monitors.
- 🔄 **Auto-Start Applications**: Automatically start selected applications at their saved positions when your PC boots.
- 🔍 **Simple and Intuitive UI**: Easily select and manage your applications with a user-friendly interface.
- 📝 **Persistent Configuration**: Your configurations are saved in a JSON file, allowing you to maintain settings across sessions.
- 🔧 **Installer Included**: Easy setup with the provided installer, which automatically registers the auto-start script.

## 🛠 Installation

1. **Download the Installer**: Get the latest release from the [Releases](#) section.
2. **Run the Installer**: Follow the prompts to install Auto App Starter on your system.
3. **Setup Auto-Start**: Use the application to select and save the apps you want to start automatically.

## 🚀 Usage

1. **Launch the Application**: Open `Auto App Starter` from your Start menu.
2. **Select Applications**: Choose the applications you want to manage from the list.
3. **Save Positions**: Arrange your applications on your monitors, then click `Record`.
4. **Enjoy!**: On your next PC boot, your selected applications will start in their saved positions.

## 📂 Configuration

All settings are stored in the `window_positions.json` and `config.json` files in the application's directory. These files store the positions of your windows and whether auto-start is enabled.

## 🛠️ Development

### Prerequisites

- Python 3.7 or higher
- Required Python libraries (listed in `requirements.txt`)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lonixchu-hk/auto-app-starter.git
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python record_positions.py
   ```

## 🤝 Contributing

We welcome contributions! If you would like to contribute, please fork the repository and submit a pull request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
