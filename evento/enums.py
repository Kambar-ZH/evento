from enum import Enum


class EventCategory(Enum):
    CINEMA = "CINEMA"
    DEVELOPMENT = "DEVELOPMENT"
    ENTARTAINMENT = "ENTARTAINMENT"
    CONCERT = "CONCERT"
    SPORT = "SPORT"
    ART = "ART"
    WORLD_EVENT = "WORLD_EVENT"
    WORKSHOP = "WORKSHOP"
    TOUR = "TOUR"
    TRIP = "TRIP"


class UserRole(Enum):
    USER = "USER"
    ORGANIZER = "ORGANIZER"
