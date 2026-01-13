#ifndef EVENT_H
#define EVENT_H

#include <Arduino.h>

enum EventSourceType {
  SERVO, LIGHT, SLIDER, CHECKBOX, BLUETOOTH, MSG_SERVICE
};

template <typename T>
class Event {
public:
  EventSourceType srcType;
  T* eventArgs;           

  Event(EventSourceType srctype, T* args) {
    srcType = srctype;
    eventArgs = args;
  }

  EventSourceType getSrcType() {
    return srcType;
  }

  T* getEventArgs() {
    return eventArgs;
  }

  ~Event() {
     // delete eventArgs; 
  }
};

#endif