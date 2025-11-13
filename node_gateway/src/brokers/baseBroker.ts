export abstract class BaseBroker {
  abstract placeOrder(order: any): Promise<any>;
  abstract cancelOrder(id: string): Promise<void>;
}