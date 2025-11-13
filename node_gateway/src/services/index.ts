/**
 * Services Registry
 * Business logic services for the Node Gateway
 */

export class ServiceRegistry {
  private services: Map<string, any> = new Map();

  register(name: string, service: any): void {
    this.services.set(name, service);
  }

  get(name: string): any {
    return this.services.get(name);
  }
}
