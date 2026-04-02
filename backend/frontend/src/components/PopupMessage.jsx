// react imports
import React from "react";

// style imports
import styles from "../styles/PopupMessage.module.css";

// cerate the popup message component with all elements defined in the hook
export default function PopupMessage({
  message,
  type = "success",
  fading,
  visible,
}) {
  return (
    <div
      className={`${styles.message} ${fading ? styles.messageFading : visible ? styles.messageVisible : ""}`}
      data-type={type}
    >
      {message}
    </div>
  );
}
