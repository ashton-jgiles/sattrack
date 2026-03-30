// import use state to create popup message hook
import { useState } from "react";

export default function usePopupMessage() {
  // popup message methods and variables
  const [message, setMessage] = useState(null);
  const [messageFading, setMessageFading] = useState(false);
  const [messageVisible, setMessageVisible] = useState(false);

  // show mesage to create our message and do its animation and timeout
  const showPopupMessage = (message, type = "success") => {
    setMessageFading(false);
    setMessage({ message, type });
    setTimeout(() => setMessageVisible(true), 10);
    setTimeout(() => {
      setMessageFading(true);
      setMessageVisible(false);
      setTimeout(() => setMessage(null), 400);
    }, 2600);
  };

  // return methods for hooking in other components
  return { message, messageFading, messageVisible, showPopupMessage };
}
