import {
  Card,
  CardContent,
  CardActions,
  CardMedia,
  Typography,
  Button,
} from "@mui/material";
import { API_URL } from "../../constants";
import { Product } from "../../types";

interface ProductCardProps {
  product: Product;
  actions: boolean;
}

export const ProductCard = (props: ProductCardProps) => (
  <Card sx={{ maxWidth: 345 }}>
    <CardMedia
      sx={{ height: 140 }}
      image={`${API_URL}/${props.product.image}`}
      title={props.product.name}
    />
    <CardContent>
      <Typography gutterBottom variant="h5" component="div">
        {props.product.name}
      </Typography>
      <Typography
        variant="body2"
        sx={{
          color: "text.secondary",
          display: "-webkit-box",
          WebkitLineClamp: 3,
          WebkitBoxOrient: "vertical",
          overflow: "hidden",
          textOverflow: "ellipsis",
          minHeight: "4.5em",
        }}
      >
        {props.product.description}
      </Typography>
    </CardContent>
    {props.actions && (
      <>
        <CardActions>
          <Button size="small" href={`#/products/${props.product.id}/show`}>
            View
          </Button>
          <Button size="small" href={`#/products/${props.product.id}`}>
            Edit
          </Button>
        </CardActions>
      </>
    )}
  </Card>
);
