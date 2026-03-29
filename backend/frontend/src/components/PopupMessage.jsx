import React from "react";
import styles from "../styles/PopupMessage.module.css";

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
