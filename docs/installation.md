# Installation Guide

## Prerequisites

- Python 3.9 or higher
- Git

## Installation Methods

### 1. GitHub Codespaces (Recommended)

1. Open the repository in GitHub Codespaces
2. Wait for the environment to be automatically set up
3. The bot will be ready to use

### 2. Local Installation

#### Clone the Repository
```bash
git clone https://github.com/Stressica1/volume-anom.git
cd volume-anom
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Install in Development Mode
```bash
pip install -e .
```

### 3. Docker Installation

```bash
# Build the Docker image
docker build -t alpine-trading-bot .

# Run the container
docker run -it alpine-trading-bot
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
BITGET_API_KEY=your_api_key_here
BITGET_API_SECRET=your_api_secret_here
BITGET_PASSPHRASE=your_passphrase_here
BITGET_SANDBOX=false
```

### Configuration File

Modify `alpine_bot/core/config.py` to adjust trading parameters:

```python
# Trading Parameters
max_positions = 20
position_size_pct = 20.0
leverage = 35
min_order_size = 10.0
```

## Verification

Test your installation:

```bash
python main.py --test
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **API Connection**: Check your API credentials
3. **Permission Errors**: Ensure proper file permissions

### Getting Help

- Check the [API Documentation](api.md)
- Review the [Configuration Guide](configuration.md)
- Open an issue on GitHub