import { Box, Button } from "@mui/material";

export const GoogleSignInButton = ({ onClick }: { onClick: () => void }) => {
  return (
    <Button
      fullWidth
      onClick={onClick}
      sx={{
        height: "40px",
        backgroundColor: "#fff",
        color: "#3c4043",
        border: "1px solid #dadce0",
        borderRadius: "4px",
        textTransform: "none",
        fontSize: "14px",
        fontWeight: 500,
        fontFamily: "Roboto, Arial, sans-serif",
        boxShadow: "none",
        "&:hover": {
          backgroundColor: "#f7f8f8",
          boxShadow: "none",
          borderColor: "#dadce0",
        },
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
        }}
      >
        <GoogleLogo />
        <span>Sign in with Google</span>
      </Box>
    </Button>
  );
};

const GoogleLogo = () => (
  <svg width="18" height="18" viewBox="0 0 48 48">
    <path
      fill="#EA4335"
      d="M24 9.5c3.54 0 6.07 1.53 7.46 2.8l5.53-5.53C33.24 3.68 28.96 1.5 24 1.5 14.73 1.5 6.9 6.98 3.27 14.92l6.44 5.01C11.43 13.6 17.2 9.5 24 9.5z"
    />
    <path
      fill="#4285F4"
      d="M46.5 24c0-1.64-.15-3.21-.43-4.73H24v9.46h12.7c-.55 2.97-2.2 5.48-4.7 7.18l7.23 5.62C43.73 37.36 46.5 31.12 46.5 24z"
    />
    <path
      fill="#FBBC05"
      d="M9.71 28.93c-.5-1.48-.78-3.06-.78-4.93s.28-3.45.78-4.93l-6.44-5.01C1.82 17.04 1 20.41 1 24s.82 6.96 2.27 9.94l6.44-5.01z"
    />
    <path
      fill="#34A853"
      d="M24 46.5c5.96 0 10.97-1.97 14.63-5.36l-7.23-5.62c-2.01 1.35-4.58 2.15-7.4 2.15-6.8 0-12.57-4.1-14.29-9.93l-6.44 5.01C6.9 41.02 14.73 46.5 24 46.5z"
    />
  </svg>
);
