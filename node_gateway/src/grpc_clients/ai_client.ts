import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';

const PROTO_PATH = path.resolve(process.cwd(), 'shared/proto/ai_service.proto');

export function createAIClient(address: string) {
  const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true,
  });

  const proto: any = grpc.loadPackageDefinition(packageDefinition).ai;
  const client = new proto.AICoreService(address, grpc.credentials.createInsecure());
  return client;
}