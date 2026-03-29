import { useState } from "react";

export default function usePopupMessage() {
  const [message, setMessage] = useState(null);
  const [messageFading, setMessageFading] = useState(false);
  const [messageVisible, setMessageVisible] = useState(false);

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

  return { message, messageFading, messageVisible, showPopupMessage };
}
