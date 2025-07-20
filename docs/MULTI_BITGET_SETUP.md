# 🔌 Multi-Bitget Account Setup

## 📊 **Overview**

Your Alpine Trading Bot now supports **two separate Bitget accounts** simultaneously! This allows you to:

- **Distribute Risk**: Spread your trading across two Bitget accounts
- **Increase Capacity**: Double your position limits and capital allocation
- **Failover Protection**: Automatic failover if one account has issues
- **Load Balancing**: Intelligent trade distribution between accounts

## 🔑 **Account Configuration**

### **Primary Bitget Account (Bitget)**
- **Priority**: 1 (Highest priority)
- **Capital Allocation**: 30%
- **Max Positions**: 3
- **API Key**: From your `.env` file
- **Status**: Primary account for trading

### **Secondary Bitget Account (Bitget2)**
- **Priority**: 2 (Second priority)
- **Capital Allocation**: 30%
- **Max Positions**: 3
- **API Key**: `bg_33b25387b50e7f874c18ddf34f5cbb14`
- **API Secret**: `4b3cab211d44a155c5cc63dd025fad43025d09155ee6eef3769ef2f6f85c9715`
- **Passphrase**: `22672267`
- **Status**: Secondary account for trading

## 🏗️ **System Architecture**

### **Load Balancing Logic**
The system uses priority-based load balancing:

1. **Primary Account (Bitget)**: First choice for all trades
2. **Secondary Account (Bitget2)**: Used when primary is at capacity
3. **Position Limits**: Respects 3-position limit per account
4. **Capital Allocation**: 30% of total capital per account
5. **Failover**: Automatic switch to secondary if primary fails

### **Trade Distribution**
```python
# Priority-based execution
if primary_account_available and primary_has_capacity:
    execute_on_primary()
elif secondary_account_available and secondary_has_capacity:
    execute_on_secondary()
else:
    reject_trade()
```

## 📊 **Capital Management**

### **Total Capital Distribution**
- **Bitget (Primary)**: 30% of total capital
- **Bitget2 (Secondary)**: 30% of total capital
- **Other Exchanges**: 40% distributed among other exchanges
- **Total Allocation**: 100% across all exchanges

### **Position Limits**
- **Per Account**: 3 positions maximum per Bitget account
- **Total Bitget**: 6 positions maximum across both accounts
- **Risk Management**: Maintains strict capital controls

## 🔍 **Monitoring and Display**

### **Exchange Summary Panel**
The Bloomberg-style interface shows both Bitget accounts:

```
🔌 EXCHANGE SUMMARY - 2/2 Connected
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ Exchange │ Status   │ Balance  │ Positions│ Priority │
├──────────┼──────────┼──────────┼──────────┼──────────┤
│ Bitget   │ ✅ ONLINE│ $150.00  │ 2        │ #1       │
│ Bitget2  │ ✅ ONLINE│ $120.00  │ 1        │ #2       │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

### **Status Indicators**
- **✅ ONLINE**: Account is connected and operational
- **❌ OFFLINE**: Account is disconnected or unavailable
- **⚠️ WARNING**: Account has issues but still functional

## 🧪 **Testing Your Setup**

### **Run the Test Script**
```bash
python test_multi_bitget.py
```

This will test:
- ✅ Connection to both Bitget accounts
- ✅ Balance fetching from both accounts
- ✅ Position monitoring for both accounts
- ✅ Trading pairs loading from primary account

### **Expected Output**
```
🧪 Testing Multi-Bitget Configuration...
============================================================
🔍 Testing Bitget (Account 1)...
✅ Bitget connection successful
💰 Bitget balance: $150.00
📊 Bitget active positions: 2
🔌 Bitget connection closed
----------------------------------------
🔍 Testing Bitget2 (Account 2)...
✅ Bitget2 connection successful
💰 Bitget2 balance: $120.00
📊 Bitget2 active positions: 1
🔌 Bitget2 connection closed
----------------------------------------
🎯 Multi-Bitget configuration test completed!
```

## 🚀 **Benefits of Multi-Bitget Setup**

### **Risk Management**
- **Diversification**: Spreads risk across two separate accounts
- **Failover Protection**: Automatic failover if one account fails
- **Capital Distribution**: Controlled capital allocation per account
- **Position Limits**: Individual position management per account

### **Performance**
- **Increased Capacity**: Double the position capacity
- **Load Balancing**: Optimal trade distribution
- **Redundancy**: Backup account for reliability
- **Scalability**: Easy to add more accounts if needed

### **Monitoring**
- **Real-time Status**: Live monitoring of both accounts
- **Balance Tracking**: Individual balance tracking per account
- **Position Monitoring**: Separate position tracking per account
- **Professional Display**: Bloomberg-style interface showing both accounts

## 🔧 **Configuration Options**

### **Priority Settings**
```python
# Primary account has highest priority
bitget_config.priority = 1    # Highest priority
bitget2_config.priority = 2   # Second priority
```

### **Capital Allocation**
```python
# Distribute capital between accounts
bitget_config.capital_allocation = 30.0   # 30% to primary
bitget2_config.capital_allocation = 30.0  # 30% to secondary
```

### **Position Limits**
```python
# Set position limits per account
bitget_config.max_positions = 3   # 3 positions on primary
bitget2_config.max_positions = 3  # 3 positions on secondary
```

## 🚨 **Emergency Procedures**

### **Account Failover**
If one Bitget account fails:
1. **Automatic Detection**: System detects connection failure
2. **Failover**: Automatically switches to other account
3. **Logging**: Detailed logging of failover events
4. **Recovery**: Automatic retry when account comes back online

### **Capital Protection**
- **Individual Limits**: Each account has its own capital limits
- **Total Protection**: Combined capital never exceeds 68%
- **Emergency Shutdown**: Triggers at 85% total capital usage
- **Position Monitoring**: Continuous monitoring of all positions

## 📈 **Performance Metrics**

### **Load Balancing Statistics**
- **Primary Account Usage**: Percentage of trades on primary account
- **Secondary Account Usage**: Percentage of trades on secondary account
- **Failover Events**: Number of times failover occurred
- **Success Rate**: Success rate per account

### **Capital Efficiency**
- **Primary Account Capital**: Capital utilization on primary account
- **Secondary Account Capital**: Capital utilization on secondary account
- **Total Capital Efficiency**: Overall capital utilization across both accounts
- **Risk Distribution**: How risk is distributed between accounts

## 🎯 **Best Practices**

### **Account Management**
1. **Monitor Both Accounts**: Regularly check both account statuses
2. **Balance Distribution**: Ensure balanced capital distribution
3. **Position Monitoring**: Monitor positions on both accounts
4. **Performance Tracking**: Track performance per account

### **Risk Management**
1. **Capital Limits**: Respect individual account capital limits
2. **Position Limits**: Don't exceed 3 positions per account
3. **Emergency Procedures**: Know what to do if one account fails
4. **Regular Testing**: Test both accounts regularly

### **Performance Optimization**
1. **Load Balancing**: Let the system distribute trades automatically
2. **Priority Management**: Primary account gets priority for important trades
3. **Capacity Planning**: Plan for maximum 6 total Bitget positions
4. **Monitoring**: Use the professional display to monitor both accounts

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Account Connection Failed**
```
❌ Failed to initialize Bitget2: Authentication failed
```
**Solution**: Verify API credentials are correct

#### **Balance Fetch Failed**
```
⚠️ Bitget2 balance fetch failed: Insufficient permissions
```
**Solution**: Check API permissions include balance reading

#### **Position Fetch Failed**
```
⚠️ Bitget2 positions fetch failed: API rate limit exceeded
```
**Solution**: Wait for rate limit to reset or reduce polling frequency

### **Testing Commands**
```bash
# Test both accounts
python test_multi_bitget.py

# Check account status
python -c "from multi_exchange_config import print_exchange_status; print_exchange_status()"

# Run the main bot
python alpine_trading_bot.py
```

## 🚀 **Next Steps**

1. **Test Configuration**: Run the test script to verify both accounts work
2. **Monitor Performance**: Watch the professional display for both accounts
3. **Adjust Settings**: Fine-tune capital allocation and position limits
4. **Scale Up**: Consider adding more accounts if needed

---

## 🎯 **Conclusion**

Your Alpine Trading Bot now has **professional multi-Bitget support** with:

1. **Dual Account Management**: Two separate Bitget accounts
2. **Intelligent Load Balancing**: Priority-based trade distribution
3. **Comprehensive Risk Management**: Individual account limits and controls
4. **Professional Monitoring**: Real-time status tracking and display
5. **Failover Protection**: Automatic failover and error recovery

This setup provides **maximum flexibility and reliability** for your trading operations!

---

*For technical implementation details and advanced configuration options, see the main codebase documentation.* 