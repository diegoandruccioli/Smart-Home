// Classe EVENT generica
#include <Arduino.h>

// Definizione del tipo EventSourceType (può essere un enum int)
enum EventSourceType {
  SERVO,
  LIGHT,
  SLIDER,
  CHECKBOX,
  BLUETOOTH,
  MSG_SERVICE
};

// Template della classe Event
template <typename T>
class Event {
public:
  EventSourceType srcType; // Tipo sorgente evento
  T* eventArgs;           // Argomenti evento di tipo T

  // Costruttore
  Event(EventSourceType srctype, T* args) {
    srcType = srctype;
    eventArgs = args;
  }

  // Getters
  EventSourceType getSrcType() {
    return srcType;
  }

  T* getEventArgs() {
    return eventArgs;
  }

  // Distruttore
  ~Event() {
    delete eventArgs; // liberiamo la memoria degli args
  }
};
