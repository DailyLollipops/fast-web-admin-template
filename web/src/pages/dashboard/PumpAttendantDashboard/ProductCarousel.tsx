import { useEffect, useState } from "react";
import { useAuthProvider, useDataProvider } from "react-admin";
import { Box, CardMedia, Typography } from "@mui/material";
import Slider from "react-slick";
import { Product } from "../../../types";
import { API_URL } from "../../../constants";

export const ProductCarousel = () => {
  const authProvider = useAuthProvider();
  const dataProvider = useDataProvider();
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    const fetchBranchProducts = async () => {
      try {
        const identity = await authProvider!.getIdentity!();
        console.log(identity);
        const products = await dataProvider.getManyToManyReferenceList(
          ["branches", "products"],
          [identity.branch_id.toString()],
        );
        console.log(products);
        setProducts(products.data);
      } catch (error) {
        console.log(error);
      }
    };

    fetchBranchProducts();
  }, [authProvider, dataProvider]);

  const settings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
    arrows: true,
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      width="100%"
      height="100%"
      maxWidth={{ xs: window.innerWidth - 100, md: 400, lg: 600 }}
      overflow="hidden"
      borderRadius={4}
      sx={{ margin: "0 auto" }}
    >
      <Typography variant="h6" mb={3} sx={{ fontWeight: "bold" }}>
        Branch Products
      </Typography>
      <Slider {...settings}>
        {products.map((product: Product) => (
          <Box
            key={product.id}
            alignContent="center"
            justifyItems="center"
            sx={{
              height: "auto",
              width: "100%",
            }}
          >
            <CardMedia
              sx={{
                height: { xs: 220, sm: 160, md: 220, lg: 220 },
                width: { xs: "100%", lg: 240 },
                objectFit: "cover",
              }}
              image={`${API_URL}/${product.image}`}
              title="Gas Station"
            />
          </Box>
        ))}
      </Slider>
    </Box>
  );
};
