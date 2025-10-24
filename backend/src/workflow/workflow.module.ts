import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config'; 
import { WorkflowController } from './workflow.controller';
import { WorkflowService } from './workflow.service';

@Module({
  imports: [ConfigModule],
  controllers: [WorkflowController],
  providers: [WorkflowService],
})
export class WorkflowModule {}