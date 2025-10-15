# Runaway Monitor - API Burn Rate Detection System

🚨 **Instantly detect runaway processes burning through your API tokens, credits, and cloud resources!**

## Overview

The Runaway Monitor is a comprehensive real-time monitoring system that tracks API usage patterns across all your connected services and immediately alerts you when anomalous behavior is detected. Perfect for preventing cost overruns, detecting runaway automation, and maintaining budget control.

## Key Features

- **Real-Time Monitoring**: Continuous polling of API usage across multiple services
- **Intelligent Detection**: Statistical analysis to identify usage spikes and patterns
- **Instant Alerts**: Telegram notifications for immediate response
- **Cost Protection**: Automatic circuit breakers to prevent runaway costs
- **Multi-Service Support**: OpenAI, GitHub Actions, Stripe, Supabase, Cloudflare R2, and more

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials and Telegram bot details
   ```

3. **Configure Monitoring**:
   ```bash
   cp config/monitor_config.example.json config/monitor_config.json
   # Adjust thresholds and monitoring intervals
   ```

4. **Test Setup**:
   ```bash
   python test_monitor.py
   ```

5. **Start Monitoring**:
   ```bash
   python monitor.py --start
   ```

## Configuration

### Environment Variables Required

```bash
# Telegram Notifications
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here

# API Credentials to Monitor
OPENAI_API_KEY=your_openai_key_here
GITHUB_TOKEN=your_github_token_here
STRIPE_API_KEY=your_stripe_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_key_here
CLOUDFLARE_API_TOKEN=your_cf_token_here
# Add more services as needed
```

### Monitoring Thresholds

Configure detection sensitivity in `config/monitor_config.json`:

```json
{
  "monitoring_interval": 300,
  "cost_thresholds": {
    "openai": {"hourly": 10.0, "daily": 100.0},
    "github_actions": {"hourly": 5.0, "daily": 50.0}
  },
  "usage_spike_multiplier": 3.0,
  "circuit_breaker": {
    "enabled": true,
    "threshold_multiplier": 5.0
  }
}
```

## Architecture

```
Runaway_Monitor/
├── monitor.py              # Main monitoring engine
├── config/
│   ├── monitor_config.json # Monitoring thresholds
│   └── thresholds.py      # Threshold management
├── detectors/
│   ├── api_detector.py    # General API usage detection
│   ├── github_detector.py # GitHub Actions monitoring
│   └── database_detector.py # Database usage monitoring
├── notifications/
│   └── telegram_notifier.py # Telegram alert system
└── test_monitor.py        # Test suite
```

## Supported Services

- **OpenAI**: Token usage and cost tracking
- **GitHub Actions**: Workflow minutes and cost monitoring
- **Stripe**: Transaction volume and processing fees
- **Supabase**: Database operations and bandwidth
- **Cloudflare R2**: Storage operations and bandwidth
- **MongoDB Atlas**: Database operations and costs
- **Vercel**: Deployment and function usage
- **Custom APIs**: Extensible framework for any REST API

## Alert Types

- **Cost Spike Alerts**: When hourly/daily costs exceed thresholds
- **Usage Pattern Alerts**: Unusual API call patterns detected
- **Circuit Breaker Alerts**: Automatic emergency stops triggered
- **Service Status Alerts**: API endpoint availability issues

## Safety Features

- **Circuit Breakers**: Automatic emergency stops when thresholds exceeded
- **Rate Limiting**: Prevents monitor itself from causing API spam
- **Graceful Degradation**: Continues monitoring even if some services fail
- **Cost Estimation**: Real-time cost projections based on current usage

## Integration with ENVThing

This system integrates seamlessly with ENVThing for credential management:

```python
# Automatic credential loading from ENVThing
monitor = RunawayMonitor(env_source="envthing")
```

## Development

### Running Tests
```bash
python test_monitor.py
```

### Adding New Service Detectors
1. Create new detector in `detectors/`
2. Extend `APIUsageDetector` class
3. Add service configuration to `monitor_config.json`
4. Update main monitor to include new detector

### Custom Thresholds
Adjust monitoring sensitivity by modifying threshold multipliers and baseline calculations in `config/thresholds.py`.

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

**⚡ Stop runaway processes before they burn through your budget!**