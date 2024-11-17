from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Tuple
from models import Schedule, Overrides, ScheduleEntry

class ScheduleCreator(ABC):
    """Abstract base class for creating schedules."""
    
    @abstractmethod
    def create_schedule(
        self,
        schedule: Schedule,
        overrides: Overrides,
        from_time: datetime,
        until_time: datetime
    ) -> List[ScheduleEntry]:
        """Create a schedule with overrides between the given times."""
        pass

class BasicScheduleCreator(ScheduleCreator):
    """Implementation such that ouptut is main schedule, with overrides put on top"""
    
    def _process_overrides(
        self,
        overrides: Overrides,
        from_time: datetime,
        until_time: datetime
    ) -> List[ScheduleEntry]:
        """Process and validate overrides within the time window."""
        override_entries: List[ScheduleEntry] = []
        
        for override in overrides.overrides:
            # Skip if override is completely outside our window
            if override.end_at <= from_time or override.start_at >= until_time:
                continue
                
            # Truncate override to our window
            entry_start = max(override.start_at, from_time)
            entry_end = min(override.end_at, until_time)
            
            override_entries.append(ScheduleEntry(
                user=override.user,
                start_at=entry_start,
                end_at=entry_end
            ))
        
        # Sort overrides by start time
        override_entries.sort(key=lambda x: x.start_at)
        return override_entries
    
    def _generate_schedule_entries(
        self,
        schedule: Schedule,
        override_entries: List[ScheduleEntry],
        from_time: datetime,
        until_time: datetime
    ) -> List[ScheduleEntry]:
        """Generate schedule entries filling gaps between overrides."""
        schedule_entries: List[ScheduleEntry] = []
        override_idx = 0
        
        # Calculate initial period and user
        interval = timedelta(days=schedule.handover_interval_days)
        periods_since_start = max(0, (from_time - schedule.handover_start_at) // interval) #handle case when negative
        user_index = int(periods_since_start) % len(schedule.users)
        
        # Iterate through periods from from_time to until_time
        current_period_start = schedule.handover_start_at + (periods_since_start * interval)
        while current_period_start < until_time:
            current_period_end = min(current_period_start + interval, until_time)
            current_user = schedule.users[user_index]
            
            # Find available time slots in this period
            available_start = max(current_period_start, from_time)
            
            # Process overrides that affect this period
            while (override_idx < len(override_entries) and 
                   override_entries[override_idx].start_at < current_period_end):
                override = override_entries[override_idx]
                
                # If there's space before this override, add an entry
                if override.start_at > available_start:
                    schedule_entries.append(ScheduleEntry(
                        user=current_user,
                        start_at=available_start,
                        end_at=override.start_at
                    ))
                
                # Move available_start to after this override
                available_start = max(available_start, override.end_at)
                override_idx += 1
            
            # If there's space after last override in this period, add an entry
            if available_start < current_period_end:
                schedule_entries.append(ScheduleEntry(
                    user=current_user,
                    start_at=available_start,
                    end_at=current_period_end
                ))
            
            # Move to next period and user
            current_period_start = current_period_end
            user_index = (user_index + 1) % len(schedule.users)
            
        return schedule_entries
    
    def create_schedule(
        self,
        schedule: Schedule,
        overrides: Overrides,
        from_time: datetime,
        until_time: datetime
    ) -> List[ScheduleEntry]:
        """Create schedule by combining overrides and regular schedule entries."""
        
        # Process overrides
        override_entries = self._process_overrides(overrides, from_time, until_time)
        
        # Generate schedule entries around overrides
        schedule_entries = self._generate_schedule_entries(
            schedule, override_entries, from_time, until_time
        )
        
        # Combine and sort all entries
        result = override_entries + schedule_entries
        result.sort(key=lambda x: x.start_at)
        return result
