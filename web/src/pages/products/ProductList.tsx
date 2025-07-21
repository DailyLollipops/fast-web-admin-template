import { List, useListContext } from "react-admin";
import { Card, Grid } from "@mui/material";
import { ProductCard } from "../../components/cards/ProductCard";
import { Product } from "../../types";

const ProductGrid = () => {
  const { data, isLoading } = useListContext();

  if (isLoading) return <>Loading...</>;
  if (!data || data.length === 0) return <>No products found.</>;

  return (
    <Grid container spacing={2} sx={{ mt: 1 }}>
      {data.map((record: Product) => (
        <Grid
          size={{ xs: 12, sm: 6, md: 4 }}
          key={record.id}
          justifyItems="center"
        >
          <ProductCard product={record} actions={true} />
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
