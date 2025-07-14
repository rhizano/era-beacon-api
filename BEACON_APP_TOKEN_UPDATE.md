# Beacon API Update: app_token Field

## Summary of Changes

This update adds a new `app_token` field to the beacons table for storing FCM (Firebase Cloud Messaging) client app tokens.

## Database Schema Changes

### Updated Beacon Table Schema:
```sql
CREATE TABLE public.beacons (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    beacon_id text NOT NULL,
    location_name text NULL,
    latitude float8 NULL,
    longitude float8 NULL,
    created_at timestamp NULL,
    updated_at timestamp NULL,
    app_token varchar(255) NULL,  -- NEW FIELD
    CONSTRAINT beacons_beacon_id_key UNIQUE (beacon_id),
    CONSTRAINT beacons_pkey PRIMARY KEY (id)
);
```

## Files Modified

### 1. Model Updates
- **app/models/beacon.py**: Added `app_token` column with String(255) type

### 2. Schema Updates
- **app/schemas/beacon.py**: 
  - Updated `BeaconBase`, `BeaconCreate`, and `BeaconUpdate` schemas
  - Added `app_token` field as optional
  - Updated examples in schema configs

### 3. Database Migrations
- **alembic/versions/001_add_app_token_to_beacons.py**: Initial table creation with app_token
- **alembic/versions/002_add_app_token_column.py**: Migration to add app_token to existing tables

### 4. Test Updates
- **tests/test_beacons.py**: 
  - Updated existing tests to include app_token
  - Added new tests for app_token functionality
  - Added test for creating beacons without app_token (optional field)

### 5. API Documentation
- **oas.beacon-api.yaml**: 
  - Updated Beacon schema definition
  - Updated request/response examples
  - Added field description for app_token

## API Changes

### Beacon Creation (POST /v1/beacons)
```json
{
  "beacon_id": "F2C56DB5-DFFB-48D2-B060-D0F5A71096E0",
  "location_name": "Cafeteria Entrance",
  "latitude": 34.052235,
  "longitude": -118.243683,
  "app_token": "eXQJ8V9K5fD:APA91bH..."  // NEW FIELD (optional)
}
```

### Beacon Update (PUT /v1/beacons/{beacon_id})
```json
{
  "location_name": "Updated Main Entrance",
  "latitude": 34.052235,
  "longitude": -118.243683,
  "app_token": "eXQJ8V9K5fD:APA91bH_updated..."  // NEW FIELD (optional)
}
```

### Beacon Response
All beacon endpoints now return the `app_token` field in the response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "beacon_id": "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0",
  "location_name": "Main Entrance",
  "latitude": 34.052235,
  "longitude": -118.243683,
  "app_token": "eXQJ8V9K5fD:APA91bH...",  // NEW FIELD
  "created_at": "2023-07-14T10:00:00Z",
  "updated_at": "2023-07-14T10:00:00Z"
}
```

## Deployment Notes

1. **Database Migration**: Run `alembic upgrade head` to apply the new migration
2. **Backward Compatibility**: The `app_token` field is optional, so existing API clients will continue to work
3. **New Functionality**: Clients can now include FCM tokens when creating or updating beacons
4. **Validation**: The `app_token` field accepts strings up to 255 characters

## Testing

Run the updated tests to verify all functionality:
```bash
pytest tests/test_beacons.py -v
```

New test cases include:
- Creating beacons with app_token
- Updating beacon app_token
- Creating beacons without app_token (optional field validation)
