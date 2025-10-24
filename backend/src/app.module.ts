import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { WorkflowModule } from './workflow/workflow.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    WorkflowModule,
  ],
})
export class AppModule {}
