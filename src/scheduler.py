from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List
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
    """Implementation where final result is as though you directly place overrides on top of orignal schedule"""
    
    def create_schedule(
        self,
        schedule: Schedule,
        overrides: Overrides,
        from_time: datetime,
        until_time: datetime
    ) -> List[ScheduleEntry]:
        """Create schedule by first adding overrides, then filling gaps with regular schedule."""
        
        # Initialize result list
        result: List[ScheduleEntry] = []
        
        # First, add all overrides that fall within our time window
        for override in overrides.overrides:
            # Skip if override is completely outside our window
            if override.end_at <= from_time or override.start_at >= until_time:
                continue
                
            # Truncate override to our window
            entry_start = max(override.start_at, from_time)
            entry_end = min(override.end_at, until_time)
            
            entry = ScheduleEntry(
                user=override.user,
                start_at=entry_start,
                end_at=entry_end
            )
            result.append(entry)
        
        # Sort overrides by start time, so that when we go through normal schedule know we can keep track of overs
        result.sort(key=lambda x: x.start_at)
        
        # Calculate initial period and user
        interval = timedelta(days=schedule.handover_interval_days)
        periods_since_start = (from_time - schedule.handover_start_at) // interval
        user_index = int(periods_since_start) % len(schedule.users)
        
        # Iterate through periods from from_time to until_time
        current_period_start = schedule.handover_start_at + (periods_since_start * interval)
        
        while current_period_start < until_time:
            current_period_end = min(current_period_start + interval, until_time)
            current_user = schedule.users[user_index]
            
            # Find available time slots in this period
            available_start = max(current_period_start, from_time)
            
            for existing in result:
                # If existing entry starts after period end, we're done with this period
                if existing.start_at >= current_period_end:
                    break
                    
                # If there's space before this override, add an entry
                if existing.start_at > available_start:
                    result.append(ScheduleEntry(
                        user=current_user,
                        start_at=available_start,
                        end_at=existing.start_at
                    ))
                
                # Move available_start to after this override
                available_start = max(available_start, existing.end_at)
            
            # If there's space after last override in this period, add an entry
            if available_start < current_period_end:
                result.append(ScheduleEntry(
                    user=current_user,
                    start_at=available_start,
                    end_at=current_period_end
                ))
            
            # Move to next period and user
            current_period_start = current_period_end
            user_index = (user_index + 1) % len(schedule.users)
        
        # Sort final result by start time
        result.sort(key=lambda x: x.start_at)
        return result
