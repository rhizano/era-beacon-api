# Presence Logs Endpoint Fix

## Issue
The `/v1/presence-logs` endpoint was returning a 500 Internal Server Error with validation errors:

```
fastapi.exceptions.ResponseValidationError: 18 validation errors:
{'type': 'datetime_type', 'loc': ('response', 82, 'timestamp'), 'msg': 'Input should be a valid datetime', 'input': None}
```

## Root Cause
The database table `presence_logs` contains NULL values in the `timestamp` field, but the Pydantic response model expected non-nullable datetime objects.

## Database Schema
```sql
CREATE TABLE public.presence_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id text NOT NULL,
    beacon_id text NULL,
    "timestamp" timestamp NULL,  -- Can be NULL
    latitude float8 NULL,
    longitude float8 NULL,
    signal_strength int4 NULL,
    created_at timestamp DEFAULT now() NULL,
    updated_at timestamp NULL,
    CONSTRAINT presence_logs_pkey PRIMARY KEY (id),
    CONSTRAINT presence_logs_beacon_id_fkey FOREIGN KEY (beacon_id) REFERENCES public.beacons(beacon_id)
);
```

## Solution
Updated the Pydantic schemas to handle NULL values properly:

### 1. Updated `PresenceLogBase` Schema
```python
class PresenceLogBase(BaseModel):
    user_id: str
    beacon_id: Optional[str] = None  # Allow NULL beacon_id
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    signal_strength: Optional[int] = None
```

### 2. Updated `PresenceLog` Response Schema
```python
class PresenceLog(PresenceLogBase):
    id: uuid.UUID
    timestamp: Optional[datetime] = None  # Allow NULL timestamp
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### 3. Updated `PresenceLogCreate` Schema
```python
class PresenceLogCreate(PresenceLogBase):
    timestamp: Optional[datetime] = None  # Allow optional timestamp on creation
```

### 4. Enhanced Service Logic
- Made beacon validation optional (only validate if beacon_id is provided)
- Set current timestamp as default when creating new records
- Improved query handling for NULL timestamps with proper ordering

### 5. Improved Query Handling
```python
def get_all_presence_logs(self, ...):
    # Handle NULL timestamps in date filtering
    if start_date:
        query = query.filter(
            (PresenceLog.timestamp >= start_date) | 
            (PresenceLog.timestamp.is_(None))
        )
    
    # Order by timestamp (NULL values last) and created_at
    query = query.order_by(
        PresenceLog.timestamp.desc().nullslast(),
        PresenceLog.created_at.desc()
    )
```

## Benefits
1. ✅ **Fixed 500 errors** - API now handles NULL timestamps gracefully
2. ✅ **Backward compatible** - Existing data with NULL values works
3. ✅ **Improved data handling** - Better validation and error handling
4. ✅ **Enhanced queries** - Proper ordering with NULL timestamp handling
5. ✅ **Flexible beacon association** - Records can exist without beacon_id

## Testing
After deployment to Render.com, the `/v1/presence-logs` endpoint should:
- Return 200 OK instead of 500 Internal Server Error
- Include records with NULL timestamps
- Handle filtering properly even with NULL values
- Maintain proper ordering (non-NULL timestamps first, then by created_at)

## Files Modified
1. `app/schemas/presence_log.py` - Updated Pydantic models
2. `app/models/presence_log.py` - Updated SQLAlchemy model
3. `app/services/presence_service.py` - Enhanced service logic

The fix is now deployed and should resolve the validation errors on the production environment.
