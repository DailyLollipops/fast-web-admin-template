import { API_URL } from "@/constants";

export const nativeLoginFlow = async (
  username: string,
  password: string,
  remember?: boolean,
) => {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const sendLoginRequest = async () => {
    let loginUrl = `${API_URL}/auth/login`;
    if (remember) {
      loginUrl += "?remember=true";
    }

    return await fetch(loginUrl, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });
  };

  const response = await sendLoginRequest();

  if (!response.ok) {
    const error = await response.json();
    return Promise.reject(error.message || "Login failed");
  }

  const data = await response.json();
  if (data.tfa_required) {
    return new Promise((resolve, reject) => {
      const popup = window.open(
        `${window.location.origin}/2fa`,
        "2FA Verification",
        "width=500,height=600",
      );
      if (!popup) return reject("Popup blocked");

      const listener = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;
        if (event.data === "login-success") {
          window.removeEventListener("message", listener);
          sendLoginRequest().then((response) => {
            if (!response.ok) {
              return reject("Login failed after 2FA");
            }
            return resolve(true);
          });
        }
      };

      window.addEventListener("message", listener);
    });
  } else {
    return Promise.resolve();
  }
};
