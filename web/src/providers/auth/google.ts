import { API_URL } from "@/constants";

export const googleLoginFlow = async (remember?: boolean) => {
  return new Promise((resolve, reject) => {
    let loginUrl = `${API_URL}/auth/google/login?next_url=${encodeURIComponent(window.location.origin)}&tfa_url=${encodeURIComponent(window.location.origin + "/2fa")}`;
    if (remember) {
      loginUrl += "&remember=true";
    }

    const popup = window.open(loginUrl, "GoogleLogin", "width=500,height=600");

    if (!popup) return reject("Popup blocked");

    const listener = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;

      if (event.data === "login-success") {
        window.removeEventListener("message", listener);
        resolve(true);
      }

      if (event.data.toString().startsWith("tfa-required?tfa_token=")) {
        window.removeEventListener("message", listener);

        const params = new URLSearchParams(event.data.split("?")[1]);
        const tfaToken = params.get("tfa_token");
        const userInfo = params.get("user_info");
        const methods = params.get("methods");
        const tfaPopup = window.open(
          `${window.location.origin}/2fa?tfa_token=${tfaToken}&user_info=${userInfo}&methods=${methods}`,
          "2FA Verification",
          "width=500,height=600",
        );

        if (!tfaPopup) return reject("2FA popup blocked");

        const tfaListener = (tfaEvent: MessageEvent) => {
          if (tfaEvent.origin !== window.location.origin) return;

          if (tfaEvent.data === "login-success") {
            window.removeEventListener("message", tfaListener);

            let loginUrl = `${API_URL}/auth/google/login_2fa`;
            if (remember) {
              loginUrl += "?remember=true";
            }

            fetch(loginUrl, {
              method: "POST",
              credentials: "include",
              headers: {
                "Content-Type": "application/json",
              },
            }).then((response) => {
              if (!response.ok) {
                reject("Login failed after 2FA");
              }
              resolve(true);
            });
          }
        };

        window.addEventListener("message", tfaListener);
      }
    };

    window.addEventListener("message", listener);
  });
};
