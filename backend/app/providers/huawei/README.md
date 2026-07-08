# Huawei Data Provider

This directory will contain the `HuaweiDataProvider` implementation.

## Status

Not implemented yet.

## Requirements

- Huawei Smart Logger API access credentials
- API endpoint URLs from Huawei
- Proper network connectivity to the Huawei inverter plant

## Implementation

When API access is received:

1. Create `huawei_provider.py` in this directory
2. Implement the `IDataProvider` interface from `app.providers.base_provider`
3. Register the provider in the service layer
4. Replace `FakeDataProvider` with `HuaweiDataProvider`

The rest of the application requires no changes because it depends only on
the `IDataProvider` abstract interface.
