# Kalshi HFT

Kalshi HFT is an open-source, high-frequency trading (HFT) framework designed for developing systematic strategies on the Kalshi exchange. Initially created as an [AISC](https://www.linkedin.com/company/ai-student-collective/posts/?feedView=all) project for market-making and cross-exchange arbitrage, the core trading system is now available for public use, customization, and expansion.

## Features

* **Kalshi Integration:** Connects to Kalshi via websocket, reads exchange packets, and maintains an accurate order book.
* **Packet Normalization:** All packets from Kalshi are normalized and timestamped.
* **Messaging with ZMQ:** Utilizes ZeroMQ (ZMQ) for efficient, scalable messaging.
* **Multi-market Support:** Capable of handling multiple Kalshi markets concurrently.
* **Extensible:** Adding new exchange connections is quick and easy 

## Installation

1. Clone this repository:

```bash
git clone <repository_url>
cd kalshi-hft
```

2. Create a `.env` file in the project root with your Kalshi credentials:

```env
KALSHI_KEY_ID=your_key_id
KALSHI_KEY_PATH=path_to_your_key
```

3. Set up the logging directory:

```bash
mkdir logging
```

4. Install dependencies (assuming Python):

```bash
pip install -r requirements.txt
```

## Usage

Run the main trading script:

```bash
python main.py
```

## Architecture
![alt text](https://raw.githubusercontent.com/AIStudentCollective/kalshi-hft/refs/heads/main/architecture.png "System Architecture")

## FAQ

### How do I add a custom strategy?
Customize your strategy logic by inheriting from ```trading_logic/strategy.py```.

### How do I add a new exchange connection?
Add new exchange connections by writing a new publisher in ```exchange_interface/publishers.py```.

### Why is this written in Python? Isn't it too slow?
Currently, Kalshi does not support colocation, so ultra-low latency isn't a practical constraint. An extra few hundred microseconds of overhead from Python is likely negligible.

## Contribution

Contributions are welcome! Feel free to fork the repository, submit pull requests, or open issues for bugs and feature requests.

## License

This project is open-source software licensed under the MIT License.

---

Created by [Isha Rawal](https://www.linkedin.com/in/isharawal/) and [Jon Levitsky](https://www.linkedin.com/in/jonathan-levitsky-807956295/). Feel free to reach out for questions, collaboration, or further development.