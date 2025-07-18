import { List, useListContext } from "react-admin";
import {
  Card,
  CardContent,
  CardActions,
  CardMedia,
  Typography,
  Button,
  Grid,
} from "@mui/material";
import { API_URL } from "../../constants";

const ProductGrid = () => {
  const { data, isLoading } = useListContext();

  if (isLoading) return <>Loading...</>;
  if (!data || data.length === 0) return <>No products found.</>;

  return (
    <Grid container spacing={2} sx={{ mt: 1 }}>
      {data.map((record) => (
        <Grid size={4} key={record.id} justifyItems="center">
          <Card sx={{ maxWidth: 345 }}>
            <CardMedia
              sx={{ height: 140 }}
              image={`${API_URL}/${record.image}`}
              title={record.name}
            />
            <CardContent>
              <Typography gutterBottom variant="h5" component="div">
                {record.name}
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
                {record.description}
              </Typography>
            </CardContent>
            <CardActions>
              <Button size="small" href={`#/products/${record.id}/show`}>
                View
              </Button>
              <Button size="small" href={`#/products/${record.id}`}>
                Edit
              </Button>
            </CardActions>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

const ListWrapper = ({ children }: { children: React.ReactNode }) => (
  <Card sx={{ padding: 3 }}>{children}</Card>
);

export const ProductList = () => (
  <List component={ListWrapper}>
    <ProductGrid />
  </List>
);
