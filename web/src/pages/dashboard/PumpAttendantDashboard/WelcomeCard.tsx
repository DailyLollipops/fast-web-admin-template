import { useGetIdentity } from "react-admin";
import { Box, Typography } from "@mui/material";
import PumpAttendant from "../../../assets/PumpAttendant.png";

export const WelcomeCard = () => {
  const { data: identity } = useGetIdentity();

  return (
    <Box
      gap={{ xs: 2, md: 4 }}
      alignItems="center"
      display="flex"
      flexDirection={{ xs: "column", md: "row" }}
      borderRadius={4}
      padding={4}
      sx={{
        backgroundColor: "#2C3E50",
        boxShadow: "0 8px 24px rgba(0, 0, 0, 0.5)",
      }}
    >
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: { xs: "center", md: "flex-start" },
          textAlign: { xs: "center", md: "left" },
        }}
      >
        <Typography
          variant="h5"
          sx={{
            color: "#ECF0F1",
            fontWeight: "bold",
          }}
        >
          Welcome back 👋
        </Typography>
        <Typography
          variant="h5"
          mb={2}
          sx={{
            color: "#2ECC71",
            fontWeight: "bold",
          }}
        >
          {identity?.name ?? "Loading"}
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: "#BDC3C7",
            marginBottom: "24px",
            maxWidth: "500px",
            lineHeight: 1.6,
          }}
        >
          Monitor your gasoline station sales with ease. Get real-time insights,
          track performance, and optimize your operations for maximum
          efficiency.
        </Typography>
      </Box>
      <Box
        display={{ xs: "none", md: "flex" }}
        justifyContent="center"
        alignItems="center"
        width={{ xs: "100%", md: "auto" }}
      >
        <img
          src={PumpAttendant}
          alt="Gas Station Pump Attendant"
          style={{
            maxWidth: "100%",
            maxHeight: "220px",
            height: "auto",
            borderRadius: "8px",
            objectFit: "contain",
            boxShadow: "0 4px 16px rgba(0, 0, 0, 0.4)",
          }}
        />
      </Box>
    </Box>
  );
};
