"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.GenerateWorkflowDto = void 0;
const class_validator_1 = require("class-validator");
class GenerateWorkflowDto {
}
exports.GenerateWorkflowDto = GenerateWorkflowDto;
__decorate([
    (0, class_validator_1.IsString)({ message: 'The prompt must be a string.' }),
    (0, class_validator_1.IsNotEmpty)({ message: 'The prompt cannot be empty.' }),
    (0, class_validator_1.Length)(10, 1000, { message: 'Prompt must be between 10 and 1000 characters.' }),
    __metadata("design:type", String)
], GenerateWorkflowDto.prototype, "prompt", void 0);
//# sourceMappingURL=generate-workflow.dto.js.map